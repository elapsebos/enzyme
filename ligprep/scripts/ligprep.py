#!/usr/bin/env python3
"""Configuration-driven RESP/RESP2 Slurm jobs. Python 3.10+."""
import argparse
import copy
import datetime
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys


ELEMENTS = ('X H He Li Be B C N O F Ne Na Mg Al Si P S Cl Ar K Ca Sc Ti V Cr Mn Fe '
            'Co Ni Cu Zn Ga Ge As Se Br Kr Rb Sr Y Zr Nb Mo Tc Ru Rh Pd Ag Cd In Sn '
            'Sb Te I Xe').split()


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def write_json(path, data):
    Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def mol2(path):
    lines = Path(path).read_text(encoding='utf-8').splitlines()
    start = lines.index('@<TRIPOS>ATOM') + 1
    stop = next(i for i in range(start, len(lines)) if lines[i].startswith('@<TRIPOS>'))
    atoms = []
    for line in lines[start:stop]:
        if not line.strip():
            continue
        fields = line.split()
        if len(fields) < 9:
            raise ValueError('MOL2 requires atom id/name/xyz/type/substructure/charge: ' + line)
        element = fields[5].split('.')[0].capitalize()
        if element not in ELEMENTS[1:]:
            raise ValueError('Unsupported MOL2 element/type: ' + fields[5])
        xyz = list(map(float, fields[2:5]))
        if not all(math.isfinite(x) for x in xyz):
            raise ValueError('Nonfinite MOL2 coordinates')
        atoms.append(dict(id=int(fields[0]), name=fields[1], element=element, xyz=xyz, fields=fields))
    if not atoms or len({a['id'] for a in atoms}) != len(atoms) or len({a['name'] for a in atoms}) != len(atoms):
        raise ValueError('MOL2 atom ids and names must be unique and nonempty')
    header = lines.index('@<TRIPOS>MOLECULE')
    counts = lines[header + 2].split()
    if int(counts[0]) != len(atoms):
        raise ValueError('MOL2 header atom count mismatch')
    bonds_start = lines.index('@<TRIPOS>BOND') + 1
    bonds = []
    for line in lines[bonds_start:]:
        if line.startswith('@<TRIPOS>'):
            break
        if line.strip():
            bonds.append(line.split())
    if len(bonds) != int(counts[1]):
        raise ValueError('MOL2 bond count mismatch')
    ids = {a['id'] for a in atoms}
    if any(int(b[1]) not in ids or int(b[2]) not in ids for b in bonds):
        raise ValueError('MOL2 bond refers to absent atom')
    if not any(a['element'] == 'H' for a in atoms):
        raise ValueError('Supply an explicit-hydrogen MOL2')
    return lines, atoms


def memory_mb(value):
    match = re.fullmatch(r'([0-9]+)(M|G|T|MB|GB|TB)?', str(value).upper())
    if not match:
        raise ValueError('Memory must be an integer in M/G/T, e.g. 32G or 24GB')
    number, unit = match.groups()
    return int(number) * {'M': 1, 'G': 1024, 'T': 1024**2, 'MB': 1, 'GB': 1024, 'TB': 1024**2, None: 1}[unit]


def positive_int(value, name):
    if type(value) is not int or value < 1:
        raise ValueError(name + ' must be a positive integer')
    return value


def validate(config):
    if config['engine'] not in ('orca', 'gaussian'):
        raise ValueError('engine must be orca or gaussian')
    slurm = config['slurm']
    for key in ('partition', 'account', 'time', 'mem'):
        value = slurm.get(key)
        if not value or re.search(r'[\s#]', str(value)):
            raise ValueError('Set slurm.' + key + ' to your fir value (no whitespace/#)')
    for key in ('qos', 'constraint', 'licenses'):
        if slurm.get(key) and re.search(r'[\s#]', str(slurm[key])):
            raise ValueError('Invalid slurm.' + key)
    for key in ('nodes', 'ntasks', 'cpus_per_task'):
        positive_int(slurm[key], 'slurm.' + key)
    if slurm['nodes'] != 1:
        raise ValueError('This pipeline supports single-node jobs only')
    env = config['environment']
    if not isinstance(env['setup_shell'], list) or not all(isinstance(s, str) for s in env['setup_shell']):
        raise ValueError('setup_shell must be a list of trusted shell commands')
    positive_int(env['omp_threads'], 'environment.omp_threads')
    if config['engine'] == 'orca':
        if slurm['cpus_per_task'] != 1 or env['omp_threads'] != 1:
            raise ValueError('ORCA uses one thread per MPI process in this pipeline')
        maxcore = positive_int(config['resources']['orca_maxcore_mb'], 'orca_maxcore_mb')
        if maxcore * slurm['ntasks'] > 0.75 * memory_mb(slurm['mem']):
            raise ValueError('ORCA maxcore * ntasks exceeds 75% of Slurm memory')
    else:
        if slurm['ntasks'] != 1:
            raise ValueError('Gaussian shared-memory jobs require ntasks=1')
        if env['omp_threads'] != slurm['cpus_per_task']:
            raise ValueError('For Gaussian, omp_threads must match cpus_per_task')
        if memory_mb(config['resources']['gaussian_memory']) >= memory_mb(slurm['mem']):
            raise ValueError('Gaussian memory must be smaller than Slurm memory')
    chem = config['chemistry']
    if chem['protocol'] not in ('RESP', 'RESP2'):
        raise ValueError('protocol must be RESP or RESP2')
    if chem['protocol'] == 'RESP':
        if config['engine'] != 'gaussian' or chem.get('fit_backend') != 'ambertools':
            raise ValueError('Traditional RESP currently requires gaussian + ambertools backend')
        if not re.search(r'\bHF/6-31G\(d\)', chem['gaussian_sp'], re.I):
            raise ValueError('This traditional RESP preset requires HF/6-31G(d) gas ESP')
        if re.search(r'scrf|cpcm|smd|solvent', chem['gaussian_sp'] + ' ' + chem['gaussian_opt'], re.I):
            raise ValueError('Traditional RESP preset must use gas-phase QM keywords')
    elif chem.get('fit_backend', 'multiwfn') != 'multiwfn':
        raise ValueError('RESP2 currently requires multiwfn backend')
    if chem['protocol'] == 'RESP2' and not 0 <= chem['delta'] <= 1:
        raise ValueError('delta must be in [0, 1]')
    for key in ('charge_tolerance', 'coordinate_tolerance_angstrom'):
        if not 0 < chem[key] <= 0.01:
            raise ValueError(key + ' must be >0 and <=0.01')
    if type(chem['optimize']) is not bool:
        raise ValueError('optimize must be a boolean')
    if not re.fullmatch(r'[A-Za-z0-9_-]+', chem['solvent']):
        raise ValueError('Invalid solvent name')
    if chem['gaussian_solvent_model'] not in ('SMD', 'IEFPCM'):
        raise ValueError('Gaussian solvent model must be SMD or IEFPCM')
    for key in ('orca_opt', 'orca_sp', 'gaussian_opt', 'gaussian_sp'):
        if not chem[key] or '\n' in chem[key] or '\r' in chem[key]:
            raise ValueError('Invalid method keyword: ' + key)
    if not config['ligands']:
        raise ValueError('No ligands configured')
    names = set()
    for ligand in config['ligands']:
        if not re.fullmatch(r'[A-Za-z0-9_-]+', ligand['id']) or ligand['id'] in names:
            raise ValueError('Ligand ids must be unique safe names')
        names.add(ligand['id'])
        if type(ligand['charge']) is not int:
            raise ValueError('Explicit integer charge is required for each ligand')
        positive_int(ligand['multiplicity'], 'multiplicity')


def sbatch_text(config, work, runner):
    slurm = config['slurm']
    directives = ['#!/bin/bash', '#SBATCH --job-name=' + config['chemistry']['protocol'].lower() + '_' + config['ligands'][0]['id']]
    for key, option in [('partition', 'partition'), ('account', 'account'), ('qos', 'qos'),
                        ('constraint', 'constraint'), ('licenses', 'licenses'), ('nodes', 'nodes'), ('ntasks', 'ntasks'),
                        ('cpus_per_task', 'cpus-per-task'), ('mem', 'mem'), ('time', 'time')]:
        if slurm.get(key) is not None:
            directives.append('#SBATCH --' + option + '=' + str(slurm[key]))
    # A separate sbatch process is launched with cwd=work; log paths are absolute.
    directives += ['#SBATCH --output=' + str(work / 'slurm-%j.out'),
                   '#SBATCH --error=' + str(work / 'slurm-%j.err'), '', 'set -euo pipefail']
    directives += config['environment']['setup_shell']
    directives += ['export OMP_NUM_THREADS=' + str(config['environment']['omp_threads']),
                   'cd ' + shlex.quote(str(work)),
                   'exec ' + shlex.quote(config['environment']['python']) + ' ' + shlex.quote(str(runner)) +
                   ' run --config ' + shlex.quote(str(work / 'config.json')), '']
    return '\n'.join(directives)


def prepare(path, submit=False, engine=None, no_optimize=False):
    path = Path(path).resolve()
    config = read_json(path)
    if engine and config['engine'] != engine:
        raise ValueError('Wrapper engine differs from configuration engine')
    if no_optimize:
        config['chemistry']['optimize'] = False
    input_root = config.get('input_directory')
    if input_root:
        directory = (path.parent / input_root).resolve()
        discovered = {f.name: f for f in directory.glob('*.mol2') if f.is_file()}
        configured = {item['input']: item for item in config['ligands']}
        unknown = set(discovered) - set(configured)
        if unknown:
            raise ValueError('Set charge/multiplicity/enabled for new input files: ' + ', '.join(sorted(unknown)))
        selected = []
        for item in config['ligands']:
            if not item.get('enabled', True):
                continue
            if item['input'] not in discovered:
                raise ValueError('Enabled ligand missing from input/: ' + item['input'])
            selected.append(dict(item, input=str(discovered[item['input']])))
        config['ligands'] = selected
    validate(config)
    inputs = []
    for ligand in config['ligands']:
        source = (path.parent / ligand['input']).resolve()
        if source.suffix.lower() != '.mol2':
            raise ValueError('Only explicit-H .mol2 inputs are supported: ' + str(source))
        _, atoms = mol2(source)
        electrons = sum(ELEMENTS.index(a['element']) for a in atoms) - ligand['charge']
        if electrons < 1 or (electrons - ligand['multiplicity'] + 1) % 2:
            raise ValueError('Charge/multiplicity is incompatible with electron count: ' + ligand['id'])
        inputs.append(source)
    root = (path.parent / config['work_root']).resolve()
    # Slurm directive paths with whitespace or % would be ambiguous; fail explicitly.
    if re.search(r'[\s%#]', str(root)):
        raise ValueError('Use a work_root without whitespace, % or #')
    root.mkdir(parents=True, exist_ok=True)
    for ligand, source in zip(config['ligands'], inputs):
        import tempfile
        work = Path(tempfile.mkdtemp(prefix=ligand['id'] + '_', dir=str(root)))
        shutil.copy2(source, work / 'input.mol2')
        snapshot = copy.deepcopy(config)
        if snapshot.get('scratch_root'):
            snapshot['scratch_root'] = str((path.parent / snapshot['scratch_root']).resolve())
        snapshot['ligands'] = [dict(ligand, input='input.mol2')]
        write_json(work / 'config.json', snapshot)
        snapshot.pop('input_directory', None)
        write_json(work / 'config.json', snapshot)
        shutil.copy2(Path(__file__).resolve(), work / 'ligprep.py')
        (work / 'job.sbatch').write_text(sbatch_text(snapshot, work, work / 'ligprep.py'), encoding='utf-8', newline='\n')
        print('Prepared:', work)
        if submit or config.get('execution', {}).get('submit', False):
            subprocess.run(['sbatch', 'job.sbatch'], cwd=str(work), check=True)


def execute(args, directory, label, stdin=None):
    with open(directory / (label + '.stdout'), 'w', encoding='utf-8') as stdout, \
            open(directory / (label + '.stderr'), 'w', encoding='utf-8') as stderr:
        subprocess.run(args, input=stdin, text=True, cwd=str(directory), stdout=stdout, stderr=stderr, check=True)


def xyz_write(path, atoms):
    text = str(len(atoms)) + '\nLigand geometry; Angstrom\n'
    text += ''.join(a['element'] + ' ' + ' '.join('%.10f' % x for x in a['xyz']) + '\n' for a in atoms)
    path.write_text(text, encoding='ascii')


def xyz_read(path):
    lines = path.read_text().splitlines()
    atoms = [dict(element=f[0].capitalize(), xyz=list(map(float, f[1:4])))
             for f in (line.split() for line in lines[2:]) if f]
    if len(atoms) != int(lines[0]) or any(len(a['xyz']) != 3 for a in atoms):
        raise ValueError('Bad XYZ geometry: ' + str(path))
    return atoms


def matching(reference, actual, tolerance=None):
    if len(reference) != len(actual):
        raise ValueError('Atom count mismatch')
    for i, (a, b) in enumerate(zip(reference, actual), 1):
        if a['element'] != b['element']:
            raise ValueError('Atom element/order mismatch at index ' + str(i))
        if not all(math.isfinite(x) for x in b['xyz']):
            raise ValueError('Nonfinite coordinates')
        if tolerance is not None and math.dist(a['xyz'], b['xyz']) > tolerance:
            raise ValueError('Charge/geometry coordinate mismatch at index ' + str(i))


def fchk_geometry(path):
    text = path.read_text().splitlines()
    def array(label):
        i = next(i for i, line in enumerate(text) if line.startswith(label))
        count = int(text[i].split('N=')[1])
        values = []
        for line in text[i + 1:]:
            values.extend(line.split())
            if len(values) >= count:
                return values[:count]
        raise ValueError('Incomplete fchk array: ' + label)
    numbers = list(map(int, array('Atomic numbers')))
    coords = [float(x.replace('D', 'E')) * 0.529177210903 for x in array('Current cartesian coordinates')]
    if len(coords) != 3 * len(numbers):
        raise ValueError('fchk coordinates mismatch')
    return [dict(element=ELEMENTS[n], xyz=coords[3*i:3*i+3]) for i, n in enumerate(numbers)]


def read_charges(path):
    values = []
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        f = line.split()
        if len(f) != 5:
            raise ValueError('Expected Multiwfn .chg: element x y z charge')
        xyz = list(map(float, f[1:4]))
        q = float(f[4])
        if not all(math.isfinite(v) for v in xyz + [q]):
            raise ValueError('Nonfinite charge data')
        values.append(dict(element=f[0].capitalize(), xyz=xyz, charge=q))
    return values


def write_charged_mol2(source, output, record):
    if source.resolve() == output.resolve() or output.exists():
        raise ValueError('Output must be a new file, distinct from input')
    if digest(source) != record['input_sha256']:
        raise ValueError('Charge record does not belong to this exact input MOL2')
    lines, atoms = mol2(source)
    fitted = record['atoms']
    matching(atoms, fitted)
    if [(a['id'], a['name']) for a in atoms] != [(a['id'], a['name']) for a in fitted]:
        raise ValueError('Charge record atom identity mismatch')
    if abs(sum(a['charge'] for a in fitted) - record['net_charge']) > record['charge_tolerance']:
        raise ValueError('Charge record net charge mismatch')
    start = lines.index('@<TRIPOS>ATOM') + 1
    counter = 0
    for i in range(start, len(lines)):
        if lines[i].startswith('@<TRIPOS>'):
            break
        if lines[i].strip():
            fields = atoms[counter]['fields'][:]
            fields[8] = '%.10f' % fitted[counter]['charge']
            lines[i] = ' '.join(fields)
            counter += 1
    header = lines.index('@<TRIPOS>MOLECULE')
    lines[header + 1] = record['protocol'] + ' fitted charges; original input geometry'
    if record['protocol'] == 'RESP2':
        lines[header + 1] += '; delta=' + str(record['delta'])
    lines[header + 4] = 'USER_CHARGES'
    output.write_text('\n'.join(lines) + '\n', encoding='utf-8')


def amber_fit(folder, programs, source, ligand, geometry, chem):
    """Two-stage AmberTools RESP on Gaussian gas-phase MK ESP."""
    _, original = mol2(source)
    execute([programs['espgen'], '-i', 'qm.stdout', '-o', 'esp.dat'], folder, 'espgen')
    lines = (folder / 'esp.dat').read_text().splitlines()
    header = lines[0].split()
    count, points = (int(header[0]), int(header[1])) if len(header) >= 2 else (int(lines[0][:5]), int(lines[0][5:10]))
    if count != len(geometry) or points < 1 or len(lines) < 1 + count + points:
        raise ValueError('Invalid Amber ESP atom/grid counts')
    esp_atoms = [dict(element=a['element'], xyz=[float(v.replace('D', 'E')) * .529177210903
                                              for v in line.split()[-3:]])
                 for a, line in zip(geometry, lines[1:1+count])]
    matching(geometry, esp_atoms, chem['coordinate_tolerance_angstrom'])
    for line in lines[1+count:1+count+points]:
        values = [float(v.replace('D', 'E')) for v in line.split()]
        if len(values) != 4 or not all(math.isfinite(v) for v in values):
            raise ValueError('Invalid Amber ESP grid values')
    execute([programs['antechamber'], '-i', str(source), '-fi', 'mol2', '-o', 'ligand.ac',
             '-fo', 'ac', '-at', 'gaff2', '-nc', str(ligand['charge']), '-s', '2'], folder, 'antechamber')
    names = [line.split()[2] for line in (folder / 'ligand.ac').read_text().splitlines()
             if line.split() and line.split()[0] == 'ATOM']
    if names != [a['name'] for a in original]:
        raise ValueError('Antechamber reordered/renamed atoms; explicit mapping is required')
    for step in (1, 2):
        execute([programs['respgen'], '-i', 'ligand.ac', '-o', 'resp%d.in' % step,
                 '-f', 'resp%d' % step], folder, 'respgen%d' % step)
        args = [programs['resp'], '-i', 'resp%d.in' % step, '-o', 'resp%d.out' % step,
                '-p', 'resp%d.punch' % step, '-e', 'esp.dat', '-t', 'qout%d' % step]
        if step == 2:
            args += ['-q', 'qout1']
        execute(args, folder, 'resp%d' % step)
    values = [float(v.replace('D', 'E')) for v in (folder / 'qout2').read_text().split()]
    if len(values) != len(geometry) or not all(math.isfinite(v) for v in values):
        raise ValueError('Amber RESP charge count or values invalid')
    if abs(sum(values) - ligand['charge']) > chem['charge_tolerance']:
        raise ValueError('Amber RESP net charge mismatch')
    return [dict(a, charge=q) for a, q in zip(geometry, values)]


def run(path):
    path = Path(path).resolve()
    config = read_json(path)
    validate(config)
    work = path.parent
    if (work / 'run_status.json').exists():
        raise ValueError('Run already started; prepare a fresh directory to retain evidence')
    ligand = config['ligands'][0]
    if len(config['ligands']) != 1:
        raise ValueError('Run requires one ligand per job snapshot')
    source = (work / ligand['input']).resolve()
    _, atoms = mol2(source)
    chem = config['chemistry']
    programs = {}
    traditional = chem['protocol'] == 'RESP'
    required = (['antechamber', 'espgen', 'respgen', 'resp'] if traditional else ['multiwfn'])
    required += ['orca', 'orca_2mkl'] if config['engine'] == 'orca' else ['gaussian', 'formchk']
    for key in required:
        program = shutil.which(config['programs'][key])
        if not program:
            raise ValueError('Executable missing from compute-node environment: ' + key)
        programs[key] = str(Path(program).resolve())
    slurm = config['slurm']
    for env, expected in [('SLURM_NTASKS', slurm['ntasks']), ('SLURM_CPUS_PER_TASK', slurm['cpus_per_task'])]:
        if os.environ.get(env) and int(os.environ[env]) != expected:
            raise ValueError(env + ' differs from configuration')
    if config.get('scratch_root'):
        import tempfile
        scratch_root = Path(config['scratch_root'])
        scratch_root.mkdir(parents=True, exist_ok=True)
        scratch = Path(tempfile.mkdtemp(prefix=work.name + '_', dir=str(scratch_root)))
    else:
        scratch = work / 'scratch'
        scratch.mkdir()
    os.environ['GAUSS_SCRDIR'] = str(scratch)
    os.environ['OMP_NUM_THREADS'] = str(config['environment']['omp_threads'])
    status = dict(state='running', started=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  input_sha256=digest(source), programs=programs, slurm_job_id=os.environ.get('SLURM_JOB_ID'),
                  gaussian_scratch=str(scratch), declared_versions=config.get('software_versions', {}))
    write_json(work / 'run_status.json', status)
    try:
        geometry = atoms
        xyz_write(work / 'initial.xyz', geometry)
        stages = (['opt'] if chem['optimize'] else []) + (['gas'] if traditional else ['gas', 'solvent'])
        charges = {}
        for stage in stages:
            folder = work / stage
            folder.mkdir()
            solvent = not traditional and stage != 'gas'
            if config['engine'] == 'orca':
                keywords = chem['orca_opt'] if stage == 'opt' else chem['orca_sp']
                text = '! ' + keywords + '\n%maxcore ' + str(config['resources']['orca_maxcore_mb'])
                text += '\n%pal nprocs ' + str(slurm['ntasks']) + ' end\n'
                if solvent:
                    text += '%cpcm\n smd true\n SMDsolvent "' + chem['solvent'] + '"\nend\n'
                text += '* xyz %d %d\n' % (ligand['charge'], ligand['multiplicity'])
                text += ''.join(a['element'] + ' ' + ' '.join('%.10f' % x for x in a['xyz']) + '\n' for a in geometry) + '*\n'
                (folder / 'job.inp').write_text(text)
                execute([programs['orca'], 'job.inp'], folder, 'qm')
                output = (folder / 'qm.stdout').read_text(errors='replace')
                if 'ORCA TERMINATED NORMALLY' not in output:
                    raise ValueError('ORCA did not terminate normally: ' + stage)
                if stage == 'opt':
                    if 'THE OPTIMIZATION HAS CONVERGED' not in output:
                        raise ValueError('ORCA geometry did not converge')
                    new_geometry = xyz_read(folder / 'job.xyz')
                else:
                    execute([programs['orca_2mkl'], 'job', '-molden'], folder, 'orca_2mkl')
                    # Multiwfn replaces only the final extension when naming .chg.
                    # Use job.molden, as in the original workflow, to obtain job.chg.
                    shutil.copy2(folder / 'job.molden.input', folder / 'job.molden')
                    wavefunction = 'job.molden'
                    menu = '7\n18\n1\ny\n0\n0\nq\n'
            else:
                keywords = chem['gaussian_opt'] if stage == 'opt' else chem['gaussian_sp']
                if solvent:
                    keywords += ' SCRF=(' + chem['gaussian_solvent_model'] + ',Solvent=' + chem['solvent'] + ')'
                if stage != 'opt':
                    keywords += ' Pop=MK IOp(6/33=2,6/42=6)'
                text = '%%chk=job.chk\n%%nprocshared=%d\n%%mem=%s\n# %s\n\nLigand %s\n\n%d %d\n' % (
                    slurm['cpus_per_task'], config['resources']['gaussian_memory'], keywords, stage,
                    ligand['charge'], ligand['multiplicity'])
                text += ''.join(a['element'] + ' ' + ' '.join('%.10f' % x for x in a['xyz']) + '\n' for a in geometry) + '\n'
                (folder / 'job.gjf').write_text(text)
                execute([programs['gaussian']], folder, 'qm', text)
                output = (folder / 'qm.stdout').read_text(errors='replace')
                if 'Normal termination' not in output or 'Error termination' in output:
                    raise ValueError('Gaussian did not terminate normally: ' + stage)
                execute([programs['formchk'], 'job.chk', 'job.fchk'], folder, 'formchk')
                if stage == 'opt':
                    if 'Optimization completed.' not in output:
                        raise ValueError('Gaussian geometry did not converge')
                    new_geometry = fchk_geometry(folder / 'job.fchk')
                else:
                    wavefunction = 'job.fchk'
                    menu = '7\n18\n8\n1\nqm.stdout\ny\n0\n0\nq\n'
            if stage == 'opt':
                matching(atoms, new_geometry)
                geometry = new_geometry
                xyz_write(work / 'optimized.xyz', geometry)
                continue
            if traditional:
                fitted = amber_fit(folder, programs, source, ligand, geometry, chem)
                charges[stage] = fitted
                continue
            (folder / 'multiwfn.stdin').write_text(menu)
            execute([programs['multiwfn'], wavefunction, '-ispecial', '1'], folder, 'multiwfn', menu)
            fitted = read_charges(folder / 'job.chg')
            matching(geometry, fitted, chem['coordinate_tolerance_angstrom'])
            if abs(sum(a['charge'] for a in fitted) - ligand['charge']) > chem['charge_tolerance']:
                raise ValueError('Fitted net charge mismatch: ' + stage)
            charges[stage] = fitted
        delta = None if traditional else chem['delta']
        if not traditional:
            matching(charges['gas'], charges['solvent'], chem['coordinate_tolerance_angstrom'])
        final = [dict(id=a['id'], name=a['name'], element=a['element'], xyz=g['xyz'],
                      charge=g['charge'] if traditional else (1-delta)*g['charge'] + delta*charges['solvent'][i]['charge'])
                 for i, (a, g) in enumerate(zip(atoms, charges['gas']))]
        record = dict(protocol=chem['protocol'], delta=delta, net_charge=ligand['charge'],
                      charge_tolerance=chem['charge_tolerance'], input_sha256=digest(source), atoms=final)
        write_json(work / 'charges.json', record)
        result = work / ('result_' + chem['protocol'] + '.mol2')
        write_charged_mol2(source, result, record)
        status.update(state='completed', output_sha256=digest(result),
                      fitted_net_charge=sum(a['charge'] for a in final),
                      coordinate_policy='original input geometry; optimized geometry saved separately')
    except Exception as exc:
        status.update(state='failed', error=str(exc))
        raise
    finally:
        status['finished'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        write_json(work / 'run_status.json', status)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    prep = sub.add_parser('prepare')
    prep.add_argument('--config', default=str(Path(__file__).resolve().parents[1] / 'config.json'))
    prep.add_argument('--submit', action='store_true')
    prep.add_argument('--engine', choices=['orca', 'gaussian'])
    prep.add_argument('--no-optimize', action='store_true')
    worker = sub.add_parser('run')
    worker.add_argument('--config', required=True)
    inject = sub.add_parser('inject-charges')
    inject.add_argument('--mol2', required=True)
    inject.add_argument('--charge-record', required=True)
    inject.add_argument('--output', required=True)
    args = parser.parse_args()
    if args.command == 'prepare':
        prepare(args.config, args.submit, args.engine, args.no_optimize)
    elif args.command == 'run':
        run(args.config)
    else:
        write_charged_mol2(Path(args.mol2), Path(args.output), read_json(args.charge_record))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as exc:
        print('ERROR:', exc, file=sys.stderr)
        sys.exit(1)
