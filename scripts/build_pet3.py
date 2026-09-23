#!/usr/bin/env python
"""Build a reproducible isolated starting conformer for 2-HE(MHET)3."""
from pathlib import Path

from rdkit import Chem
from rdkit.Chem import AllChem, rdMolDescriptors
from pet3_spec import CONFORMER_SEED, EXPECTED_ATOMS, EXPECTED_FORMULA, SMILES


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "structures" / "PET3"
OUT.mkdir(parents=True, exist_ok=True)

mol = Chem.MolFromSmiles(SMILES)
if mol is None:
    raise ValueError("Could not parse the PET3 SMILES")
mol = Chem.AddHs(mol)
formula = rdMolDescriptors.CalcMolFormula(mol)
if formula != EXPECTED_FORMULA or mol.GetNumAtoms() != EXPECTED_ATOMS:
    raise ValueError(f"Structure mismatch: formula={formula}, atoms={mol.GetNumAtoms()}")

params = AllChem.ETKDGv3()
params.randomSeed = CONFORMER_SEED
params.useRandomCoords = True
if AllChem.EmbedMolecule(mol, params) != 0:
    raise RuntimeError("RDKit conformer embedding failed")
if AllChem.MMFFOptimizeMolecule(mol, mmffVariant="MMFF94s", maxIters=2000) != 0:
    raise RuntimeError("RDKit MMFF optimization did not converge")

props = AllChem.MMFFGetMoleculeProperties(mol, mmffVariant="MMFF94s")
energy = AllChem.MMFFGetMoleculeForceField(mol, props).CalcEnergy()
mol.SetProp("_Name", "2-HE(MHET)3 isolated MMFF94s starting conformer")
mol.SetProp("SMILES", SMILES)
mol.SetProp("Formula", formula)
mol.SetProp("AtomCountIncludingHydrogen", str(mol.GetNumAtoms()))
mol.SetProp("MMFF94sEnergy_kcal_mol", f"{energy:.6f}")
mol.SetProp("ConformerSeed", str(CONFORMER_SEED))

writer = Chem.SDWriter(str(OUT / "2-HE-MHET3_initial_mmff.sdf"))
writer.write(mol)
writer.close()
(OUT / "2-HE-MHET3.smi").write_text(f"{SMILES}\t2-HE(MHET)3\n", encoding="utf-8")
print(f"formula={formula}; atoms={mol.GetNumAtoms()}; MMFF94s_energy_kcal_mol={energy:.6f}")
