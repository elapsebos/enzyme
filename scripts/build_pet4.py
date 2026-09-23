#!/usr/bin/env python
"""Build a reproducible isolated starting conformer for the PET4 candidate."""
from pathlib import Path

from rdkit import Chem
from rdkit.Chem import AllChem, rdMolDescriptors
from pet3_spec import CONFORMER_SEED, PET4_ATOMS, PET4_FORMULA, PET4_SMILES


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "structures" / "PET4"
OUT.mkdir(parents=True, exist_ok=True)

mol = Chem.AddHs(Chem.MolFromSmiles(PET4_SMILES))
formula = rdMolDescriptors.CalcMolFormula(mol)
if formula != PET4_FORMULA or mol.GetNumAtoms() != PET4_ATOMS:
    raise ValueError(f"Structure mismatch: formula={formula}, atoms={mol.GetNumAtoms()}")

params = AllChem.ETKDGv3()
params.randomSeed = CONFORMER_SEED
params.useRandomCoords = True
if AllChem.EmbedMolecule(mol, params) != 0:
    raise RuntimeError("RDKit conformer embedding failed")
if AllChem.MMFFOptimizeMolecule(mol, mmffVariant="MMFF94s", maxIters=3000) != 0:
    raise RuntimeError("RDKit MMFF optimization did not converge")

props = AllChem.MMFFGetMoleculeProperties(mol, mmffVariant="MMFF94s")
energy = AllChem.MMFFGetMoleculeForceField(mol, props).CalcEnergy()
mol.SetProp("_Name", "2-HE(MHET)4 provisional PET4 starting conformer")
mol.SetProp("SMILES", PET4_SMILES)
mol.SetProp("Formula", formula)
mol.SetProp("AtomCountIncludingHydrogen", str(mol.GetNumAtoms()))
mol.SetProp("MMFF94sEnergy_kcal_mol", f"{energy:.6f}")
mol.SetProp("ConformerSeed", str(CONFORMER_SEED))

writer = Chem.SDWriter(str(OUT / "2-HE-MHET4_initial_mmff.sdf"))
writer.write(mol)
writer.close()
(OUT / "2-HE-MHET4.smi").write_text(f"{PET4_SMILES}\t2-HE(MHET)4\n", encoding="utf-8")
print(f"formula={formula}; atoms={mol.GetNumAtoms()}; MMFF94s_energy_kcal_mol={energy:.6f}")
