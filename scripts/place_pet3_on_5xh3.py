#!/usr/bin/env python
"""Align the central PET3 unit to the HEMT pose in 5XH3 and map to 6EQE."""
from pathlib import Path
import argparse

import numpy as np
from Bio import Align
from Bio.PDB import MMCIFParser, PDBParser
from Bio.PDB.Superimposer import SVDSuperimposer
from Bio.SeqUtils import seq1
from rdkit import Chem
from rdkit.Chem import AllChem, rdMolDescriptors
from pet3_spec import (
    CONFORMER_SEED, EXPECTED_ATOMS, EXPECTED_FORMULA, HEMT_TO_PET3, SMILES,
    PET4_ATOMS, PET4_FORMULA, PET4_SMILES,
    SCISSILE_CARBONYL_C, SCISSILE_CARBONYL_O, SCISSILE_ESTER_O,
)


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "structures" / "raw"
PREPARED = ROOT / "structures" / "prepared"
def chain_and_residues(path):
    structure = MMCIFParser(QUIET=True).get_structure(path.stem, str(path))
    chain = structure[0]["A"]
    residues = [r for r in chain if r.id[0] == " " and seq1(r.resname, custom_map={"UNK": "X"}) != "X"]
    sequence = "".join(seq1(r.resname) for r in residues)
    return chain, residues, sequence


def protein_transform():
    c6, r6, s6 = chain_and_residues(RAW / "6EQE.cif")
    c5, r5, s5 = chain_and_residues(RAW / "5XH3.cif")
    aligner = Align.PairwiseAligner()
    aligner.mode = "global"
    aligner.match_score, aligner.mismatch_score = 2, -1
    aligner.open_gap_score, aligner.extend_gap_score = -5, -0.5
    alignment = aligner.align(s6, s5)[0]
    fixed, moving = [], []
    for (a, b), (c, d) in zip(*alignment.aligned):
        for i, j in zip(range(a, b), range(c, d)):
            if "CA" in r6[i] and "CA" in r5[j]:
                fixed.append(r6[i]["CA"].coord)
                moving.append(r5[j]["CA"].coord)
    sup = SVDSuperimposer()
    sup.set(np.asarray(fixed), np.asarray(moving))
    sup.run()
    return sup.get_rotran(), sup.get_rms(), c6


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--units", type=int, choices=(3, 4), default=3)
    units = parser.parse_args().units
    smiles, formula, atom_count = (
        (SMILES, EXPECTED_FORMULA, EXPECTED_ATOMS)
        if units == 3
        else (PET4_SMILES, PET4_FORMULA, PET4_ATOMS)
    )
    out = ROOT / "structures" / f"PET{units}"
    out.mkdir(parents=True, exist_ok=True)
    mol = Chem.AddHs(Chem.MolFromSmiles(smiles))
    if rdMolDescriptors.CalcMolFormula(mol) != formula or mol.GetNumAtoms() != atom_count:
        raise ValueError("PET3 formula or atom count mismatch")
    params = AllChem.ETKDGv3()
    params.randomSeed = CONFORMER_SEED
    params.useRandomCoords = True
    if AllChem.EmbedMolecule(mol, params) != 0:
        raise RuntimeError("Could not embed PET3 conformer")
    if AllChem.MMFFOptimizeMolecule(mol, mmffVariant="MMFF94s", maxIters=2000) != 0:
        raise RuntimeError("PET3 conformer minimization did not converge")

    conf = mol.GetConformer()
    pet_coords = np.asarray(conf.GetPositions())
    crystal, _, _ = chain_and_residues(RAW / "5XH3.cif")
    hemt = next(r for r in crystal if r.resname == "856")
    atom_names = list(HEMT_TO_PET3)
    target = np.asarray([hemt[name].coord for name in atom_names])
    moving = np.asarray([pet_coords[HEMT_TO_PET3[name]] for name in atom_names])
    ligand_sup = SVDSuperimposer()
    ligand_sup.set(target, moving)
    ligand_sup.run()
    ligand_rotation, ligand_translation = ligand_sup.get_rotran()
    anchored_5xh3 = pet_coords @ ligand_rotation + ligand_translation
    ligand_fit_rmsd = ligand_sup.get_rms()
    all_template_names = list(HEMT_TO_PET3)
    all_template_coords = np.asarray([hemt[name].coord for name in all_template_names])
    all_mapped_coords = np.asarray(
        [anchored_5xh3[HEMT_TO_PET3[name]] for name in all_template_names]
    )
    full_fragment_rmsd = ligand_sup.get_rms()
    core_names = ["C05", "C06", "C07", "C08", "C15", "C16", "C09", "O10", "O11"]
    core_delta = np.asarray([
        anchored_5xh3[HEMT_TO_PET3[name]] - hemt[name].coord for name in core_names
    ])
    core_fit_rmsd = float(np.sqrt(np.mean(np.sum(core_delta ** 2, axis=1))))

    (protein_rotation, protein_translation), protein_rmsd, _ = protein_transform()
    in_6eqe = anchored_5xh3 @ protein_rotation + protein_translation
    for i, xyz in enumerate(in_6eqe):
        conf.SetAtomPosition(i, xyz.tolist())

    mol.SetProp("_Name", f"2-HE(MHET){units} aligned to central HEMT-like unit in 5XH3")
    mol.SetProp("Formula", formula)
    mol.SetProp("AtomCountIncludingHydrogen", str(atom_count))
    mol.SetProp("Template", "5XH3 HEMT, component 856")
    mol.SetProp("ReferenceProtein", "6EQE chain A")
    mol.SetProp("TemplateFitRMSD_A", f"{ligand_fit_rmsd:.4f}")
    mol.SetProp("ProteinAlignmentRMSD_A", f"{protein_rmsd:.4f}")
    mol.SetProp("ScissileCarbonylC_PET3AtomIndex", str(SCISSILE_CARBONYL_C))
    mol.SetProp("ScissileCarbonylO_PET3AtomIndex", str(SCISSILE_CARBONYL_O))
    mol.SetProp("ScissileEsterO_PET3AtomIndex", str(SCISSILE_ESTER_O))
    stem = f"2-HE-MHET{units}"
    Chem.MolToMolFile(mol, str(out / f"{stem}_5XH3_pose_seed.mol"))
    Chem.MolToMolFile(mol, str(out / f"{stem}_5XH3_pose_seed.sdf"))
    Chem.MolToPDBFile(mol, str(out / f"{stem}_5XH3_pose_seed.pdb"))

    protein = PDBParser(QUIET=True).get_structure(
        "6EQE", str(PREPARED / "6EQE_WT_chainA_heavy.pdb")
    )
    protein_coords = np.asarray([a.coord for a in protein.get_atoms() if a.element not in {"H", "D"}])
    heavy_coords = in_6eqe[:mol.GetNumHeavyAtoms()]
    distances = np.linalg.norm(heavy_coords[:, None, :] - protein_coords[None, :, :], axis=2)
    min_distance = float(distances.min())
    n_under_2 = int((distances < 2.0).sum())
    n_under_25 = int((distances < 2.5).sum())
    active_site = protein[0]["A"]
    ser160_og = active_site[(" ", 160, " ") ]["OG"].coord
    tyr87_n = active_site[(" ", 87, " ") ]["N"].coord
    met161_n = active_site[(" ", 161, " ") ]["N"].coord
    ser_c_distance = float(np.linalg.norm(heavy_coords[SCISSILE_CARBONYL_C] - ser160_og))
    tyr_o_distance = float(np.linalg.norm(heavy_coords[SCISSILE_CARBONYL_O] - tyr87_n))
    met_o_distance = float(np.linalg.norm(heavy_coords[SCISSILE_CARBONYL_O] - met161_n))

    report = f"""# PET{units} initial-pose seed QC

This is an initial geometric seed, not a relaxed enzyme-substrate complex or an MD-ready input.

- Ligand: 2-HE(MHET){units}; {formula}; {atom_count} atoms including hydrogens.
- Alignment template: HEMT component 856 in 5XH3 chain A.
- Mapped PET3 central terephthalate unit onto the HEMT aromatic ring and ester groups.
- HEMT atoms used: {', '.join(atom_names)}.
- All mapped local HEMT/PET3-fragment fit RMSD: {full_fragment_rmsd:.3f} Å.
- Central ring/reactive-carbonyl RMSD within that fit: {core_fit_rmsd:.3f} Å.
- 5XH3-to-6EQE protein C-alpha alignment RMSD: {protein_rmsd:.3f} Å.
- Ser160 OG to scissile carbonyl C distance: {ser_c_distance:.3f} Å.
- Oxyanion carbonyl O to Tyr87 N / Met161 N distances: {tyr_o_distance:.3f} / {met_o_distance:.3f} Å.
- Closest ligand/protein heavy-atom distance: {min_distance:.3f} Å.
- Ligand/protein heavy-atom pairs under 2.0 Å: {n_under_2}; under 2.5 Å: {n_under_25}.
- The scissile carbonyl in the chosen seed is PET3 atom index {SCISSILE_CARBONYL_C}, oxygen index {SCISSILE_CARBONYL_O}, ester oxygen index {SCISSILE_ESTER_O} (zero-based RDKit atom indices).

Review this pose visually and inspect clashes, torsions, oxyanion-hole geometry, and the Ser160 nucleophile distance before restrained relaxation. The HEMT structure is a catalytically inactive mutant, so this template constrains binding geometry but does not supply a WT catalytic state.
"""
    report_name = "initial_pose_qc.md" if units == 3 else "initial_pose_qc_pet4.md"
    (ROOT / "docs" / report_name).write_text(report, encoding="utf-8")
    print(f"all_local_atoms_fit_rmsd_A={full_fragment_rmsd:.3f}; core_rmsd_in_fit_A={core_fit_rmsd:.3f}")
    print(f"protein_alignment_rmsd_A={protein_rmsd:.3f}")
    print(f"Ser160_OG_to_scissile_C_A={ser_c_distance:.3f}")
    print(f"oxyanionO_to_Tyr87N_A={tyr_o_distance:.3f}; to_Met161N_A={met_o_distance:.3f}")
    print(f"min_heavy_atom_distance_A={min_distance:.3f}")
    print(f"pairs_under_2A={n_under_2}; pairs_under_2_5A={n_under_25}")


if __name__ == "__main__":
    main()
