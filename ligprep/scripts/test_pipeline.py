import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('pipeline', ROOT / 'ligprep.py')
p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)
INPUT = ROOT.parent / 'input/HEMT.mol2'


class PipelineChecks(unittest.TestCase):
    def config(self):
        c = p.read_json(ROOT.parent / 'config.resp2.example.json')
        c.pop('input_directory', None)
        c['slurm'].update(partition='test', account='test')
        c['ligands'] = [dict(id='HEMT', input=str(INPUT), charge=0, multiplicity=1)]
        return c

    def test_configuration_blocks_unknown_cluster_and_oversubscription(self):
        c = self.config()
        p.validate(c)
        c['slurm']['account'] = None
        with self.assertRaises(ValueError): p.validate(c)
        c = self.config()
        c['resources']['orca_maxcore_mb'] = 4000
        with self.assertRaises(ValueError): p.validate(c)
        c = self.config()
        c['engine'] = 'gaussian'
        with self.assertRaises(ValueError): p.validate(c)

    def test_unique_job_preparation_and_explicit_negative_charge(self):
        with tempfile.TemporaryDirectory() as tmp:
            c = self.config()
            c['work_root'] = str(Path(tmp) / 'jobs')
            config = Path(tmp) / 'config.json'
            p.write_json(config, c)
            before = INPUT.read_bytes()
            p.prepare(config)
            p.prepare(config)
            jobs = list((Path(tmp) / 'jobs').iterdir())
            self.assertEqual(len(jobs), 2)
            self.assertEqual(INPUT.read_bytes(), before)
            for job in jobs:
                self.assertEqual(p.digest(job / 'input.mol2'), p.digest(INPUT))
                script = (job / 'job.sbatch').read_text()
                self.assertIn('--ntasks=16', script)
                self.assertIn(str(job / 'slurm-%j.out'), script)
                self.assertEqual((job / 'ligprep.py').read_bytes(), Path(p.__file__).read_bytes())
            # Charged species must retain their explicit state through submission.
            c['ligands'][0]['input'] = str(ROOT.parents[1] / 'structures/ligands/MHET_C9C/MHET_QM_start_anion.mol2')
            c['ligands'][0]['charge'] = -1
            c['ligands'][0]['multiplicity'] = 1
            p.write_json(config, c)
            p.prepare(config)
            snapshots = [p.read_json(j / 'config.json') for j in (Path(tmp) / 'jobs').iterdir()]
            self.assertIn(-1, [s['ligands'][0]['charge'] for s in snapshots])

    def fake_engine(self, args, folder, label, stdin=None):
        folder = Path(folder)
        _, atoms = p.mol2(folder.parent / 'input.mol2')
        if label == 'qm':
            (folder / 'qm.stdout').write_text('ORCA TERMINATED NORMALLY\nTHE OPTIMIZATION HAS CONVERGED\n')
            if folder.name == 'opt': p.xyz_write(folder / 'job.xyz', atoms)
        elif label == 'orca_2mkl':
            (folder / 'job.molden.input').write_text('mock')
        elif label == 'multiwfn':
            self.assertTrue((folder / args[1]).exists())
            charge = 0.2 if folder.name == 'gas' else 0.4
            text = ''.join('%s %.10f %.10f %.10f %.10f\n' % (a['element'], *a['xyz'], charge if i == 0 else -charge if i == 1 else 0)
                           for i, a in enumerate(atoms))
            (folder / 'job.chg').write_text(text)
            (folder / 'multiwfn.stdout').write_text('mock fitting only')

    def test_mock_orca_flow_charge_mix_and_input_preservation(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            source = folder / 'input.mol2'
            source.write_bytes(INPUT.read_bytes())
            c = self.config()
            c['ligands'][0]['input'] = 'input.mol2'
            config = folder / 'config.json'
            p.write_json(config, c)
            before = p.digest(source)
            with patch.object(p.shutil, 'which', return_value=sys.executable), patch.object(p, 'execute', side_effect=self.fake_engine):
                p.run(config)
            self.assertEqual(p.digest(source), before)
            self.assertEqual(p.read_json(folder / 'run_status.json')['state'], 'completed')
            self.assertAlmostEqual(p.read_json(folder / 'charges.json')['atoms'][0]['charge'], .3)
            lines, atoms = p.mol2(folder / 'result_RESP2.mol2')
            self.assertEqual(float(atoms[0]['fields'][8]), .3)
            self.assertIn('USER_CHARGES', lines)
            self.assertNotIn('placeholder', lines[1])
            self.assertTrue((folder / 'gas/job.chg').exists())
            self.assertTrue((folder / 'solvent/job.chg').exists())
            record = p.read_json(folder / 'charges.json')
            with self.assertRaises(ValueError):
                p.write_charged_mol2(source, source, record)
            with self.assertRaises(ValueError):
                p.write_charged_mol2(source, folder / 'result_RESP2.mol2', record)
            altered = folder / 'altered.mol2'
            altered.write_bytes(source.read_bytes() + b'\n')
            with self.assertRaises(ValueError):
                p.write_charged_mol2(altered, folder / 'bad.mol2', record)
            with self.assertRaises(ValueError): p.run(config)

    def test_failed_fitting_retains_logs_and_blocks_final_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            (folder / 'input.mol2').write_bytes(INPUT.read_bytes())
            c = self.config()
            c['ligands'][0]['input'] = 'input.mol2'
            p.write_json(folder / 'config.json', c)
            def bad_fit(args, stage, label, stdin=None):
                self.fake_engine(args, stage, label, stdin)
                if label == 'multiwfn':
                    path = stage / 'job.chg'
                    lines = path.read_text().splitlines()
                    fields = lines[0].split()
                    fields[-1] = '0.9'
                    lines[0] = ' '.join(fields)
                    path.write_text('\n'.join(lines) + '\n')
            with patch.object(p.shutil, 'which', return_value=sys.executable), patch.object(p, 'execute', side_effect=bad_fit):
                with self.assertRaises(ValueError): p.run(folder / 'config.json')
            self.assertEqual(p.read_json(folder / 'run_status.json')['state'], 'failed')
            self.assertFalse((folder / 'result_RESP2.mol2').exists())
            self.assertTrue((folder / 'gas/job.chg').exists())

    def test_atom_reordering_and_invalid_numbers_are_rejected(self):
        _, atoms = p.mol2(INPUT)
        changed = copy.deepcopy(atoms)
        changed[0], changed[3] = changed[3], changed[0]
        with self.assertRaises(ValueError): p.matching(atoms, changed, .005)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'bad.chg'
            path.write_text('C 0 0 0 nan\n')
            with self.assertRaises(ValueError): p.read_charges(path)

    def test_gaussian_layout_and_fchk_unit_conversion(self):
        c = self.config()
        c['engine'] = 'gaussian'
        c['slurm'].update(ntasks=1, cpus_per_task=16)
        c['environment']['omp_threads'] = 16
        p.validate(c)
        self.assertIn('--cpus-per-task=16', p.sbatch_text(c, Path('/jobs/a'), Path('/jobs/a/run.py')))
        with tempfile.TemporaryDirectory() as tmp:
            file = Path(tmp) / 'sample.fchk'
            file.write_text('Atomic numbers                            I   N=           2\n 6 1\nCurrent cartesian coordinates              R   N=           6\n 0 0 0 2 0 0\n')
            atoms = p.fchk_geometry(file)
            self.assertAlmostEqual(atoms[1]['xyz'][0], 1.058354421806)

    def test_mock_gaussian_end_to_end_and_noopt(self):
        for optimize in (True, False):
            with tempfile.TemporaryDirectory() as tmp:
                folder = Path(tmp)
                (folder / 'input.mol2').write_bytes(INPUT.read_bytes())
                c = self.config()
                c['engine'] = 'gaussian'
                c['slurm'].update(ntasks=1, cpus_per_task=16)
                c['environment']['omp_threads'] = 16
                c['chemistry']['optimize'] = optimize
                c['ligands'][0]['input'] = 'input.mol2'
                p.write_json(folder / 'config.json', c)
                def gaussian_mock(args, stage, label, stdin=None):
                    _, atoms = p.mol2(folder / 'input.mol2')
                    if label == 'qm':
                        (stage / 'qm.stdout').write_text('Normal termination\nOptimization completed.\n')
                    elif label == 'formchk':
                        numbers = ' '.join(str(p.ELEMENTS.index(a['element'])) for a in atoms)
                        coords = ' '.join(str(x / .529177210903) for a in atoms for x in a['xyz'])
                        (stage / 'job.fchk').write_text('Atomic numbers I N= %d\n%s\nCurrent cartesian coordinates R N= %d\n%s\n' % (len(atoms), numbers, len(atoms)*3, coords))
                    else:
                        self.fake_engine(args, stage, label, stdin)
                with patch.object(p.shutil, 'which', return_value=sys.executable), patch.object(p, 'execute', side_effect=gaussian_mock):
                    p.run(folder / 'config.json')
                self.assertEqual(p.read_json(folder / 'run_status.json')['state'], 'completed')
                route = (folder / 'gas/job.gjf').read_text()
                self.assertIn('%nprocshared=16', route)
                self.assertIn('%mem=24GB', route)
                self.assertEqual((folder / 'optimized.xyz').exists(), optimize)

    def test_input_folder_discovery_unknown_files_and_disabled_selection(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'input').mkdir()
            (root / 'input/HEMT.mol2').write_bytes(INPUT.read_bytes())
            (root / 'input/new.mol2').write_bytes(INPUT.read_bytes())
            c = self.config()
            c.update(input_directory='input', work_root='output')
            c['ligands'][0]['input'] = 'HEMT.mol2'
            path = root / 'config.json'
            p.write_json(path, c)
            with self.assertRaisesRegex(ValueError, 'new input files'): p.prepare(path)
            self.assertFalse((root / 'output').exists())
            c['ligands'].append(dict(id='new', input='new.mol2', enabled=False, charge=0, multiplicity=1))
            p.write_json(path, c)
            p.prepare(path)
            jobs = list((root / 'output').iterdir())
            self.assertEqual(len(jobs), 1)
            self.assertNotIn('input_directory', p.read_json(jobs[0] / 'config.json'))

    def test_traditional_resp_gaussian_ambertools_flow(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            (folder / 'input.mol2').write_bytes(INPUT.read_bytes())
            c = p.read_json(ROOT.parent / 'config.example.json')
            c.pop('input_directory', None)
            c['slurm'].update(partition='test', account='test')
            c['ligands'] = [dict(id='HEMT', input='input.mol2', charge=0, multiplicity=1)]
            p.write_json(folder / 'config.json', c)
            _, atoms = p.mol2(INPUT)
            def mock(args, stage, label, stdin=None):
                if label == 'qm':
                    (stage / 'qm.stdout').write_text('Normal termination\nOptimization completed.\n')
                elif label == 'formchk':
                    numbers = ' '.join(str(p.ELEMENTS.index(a['element'])) for a in atoms)
                    coords = ' '.join(str(x / .529177210903) for a in atoms for x in a['xyz'])
                    (stage / 'job.fchk').write_text('Atomic numbers I N= %d\n%s\nCurrent cartesian coordinates R N= %d\n%s\n' % (len(atoms), numbers, len(atoms)*3, coords))
                elif label == 'espgen':
                    coords = ''.join(' '.join(str(x / .529177210903) for x in a['xyz']) + '\n' for a in atoms)
                    (stage / 'esp.dat').write_text('%d 1\n' % len(atoms) + coords + '0 0 0 1\n')
                elif label == 'antechamber':
                    (stage / 'ligand.ac').write_text(''.join('ATOM %d %s\n' % (a['id'], a['name']) for a in atoms))
                elif label.startswith('respgen'):
                    (stage / args[args.index('-o')+1]).write_text('mock fitting input')
                elif label in ('resp1', 'resp2'):
                    q = [.2, -.2] + [0.] * (len(atoms)-2)
                    (stage / args[args.index('-t')+1]).write_text(' '.join(map(str, q)))
                else:
                    raise AssertionError('Unexpected stage, including Multiwfn: ' + label)
            with patch.object(p.shutil, 'which', return_value=sys.executable), patch.object(p, 'execute', side_effect=mock):
                p.run(folder / 'config.json')
            self.assertTrue((folder / 'result_RESP.mol2').exists())
            self.assertFalse((folder / 'solvent').exists())
            record = p.read_json(folder / 'charges.json')
            self.assertEqual(record['protocol'], 'RESP')
            self.assertIsNone(record['delta'])
            for stage in ('gas', 'opt'):
                text = (folder / stage / 'job.gjf').read_text()
                self.assertIn('HF/6-31G(d)', text)
                self.assertNotIn('SCRF', text)
            self.assertTrue((folder / 'gas/resp2.in').exists())


if __name__ == '__main__':
    unittest.main()
