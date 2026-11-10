#!/usr/bin/env python
"""Extract experimental HEMT/C9C coordinates and build an MHET anion model."""
from pathlib import Path

from Bio.PDB import MMCIFParser, PDBIO, Select
from rdkit import Chem
from rdkit.Chem import AllChem


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "structures" / "raw"
OUT = ROOT / "structures" / "ligands"


class ComponentSelect(Select):
    def __init__(self, chain_id, resname):
        self.chain_id = chain_id
        self.resname = resname

    def accept_chain(self, chain):
        return chain.id == self.chain_id

    def accept_residue(self, residue):
        return residue.resname == self.resname


def extract(pdb_id, component, chain_id, output):
    structure = MMCIFParser(QUIET=True).get_structure(
        pdb_id, str(RAW / f"{pdb_id}.cif")
    )
    residues = [
        residue for residue in structure[0][chain_id]
        if residue.resname == component
    ]
    if len(residues) != 1:
        raise RuntimeError(
            f"Expected one {component} in {pdb_id} chain {chain_id}; found {len(residues)}"
        )
    writer = PDBIO()
    writer.set_structure(structure)
    writer.save(str(output), ComponentSelect(chain_id, component))


def write_mhet_anion(path):
    mol = Chem.AddHs(Chem.MolFromSmiles("OCCOC(=O)c1ccc(cc1)C(=O)[O-]"))
    params = AllChem.ETKDGv3()
    params.randomSeed = 20261111
    params.useRandomCoords = True
    if AllChem.EmbedMolecule(mol, params) != 0:
        raise RuntimeError("Could not embed MHET anion")
    if AllChem.MMFFOptimizeMolecule(mol, mmffVariant="MMFF94s", maxIters=2000) != 0:
        raise RuntimeError("MHET anion MMFF94s optimization did not converge")
    mol.SetProp("_Name", "MHET monoanion; RDKit MMFF94s starting conformer")
    mol.SetProp("SMILES", "OCCOC(=O)c1ccc(cc1)C(=O)[O-]")
    mol.SetProp("FormalCharge", "-1")
    mol.SetProp("ConformerSeed", str(params.randomSeed))
    writer = Chem.SDWriter(str(path))
    writer.write(mol)
    writer.close()


def main():
    hems = OUT / "HEMT_856"
    mhet = OUT / "MHET_C9C"
    hems.mkdir(parents=True, exist_ok=True)
    mhet.mkdir(parents=True, exist_ok=True)

    extract("5XH3", "856", "A", hems / "HEMT_5XH3_crystal_pose.pdb")
    extract("7XTW", "C9C", "A", mhet / "MHET_C9C_7XTW_crystal_pose.pdb")
    write_mhet_anion(mhet / "MHET_C9C_anion_MMFF94s_start.sdf")

    for path in (hems / "856_ideal.sdf", mhet / "C9C_ideal.sdf"):
        mol = Chem.SDMolSupplier(str(path), removeHs=False)[0]
        if mol is None:
            raise RuntimeError(f"Could not read {path}")
        print(path.name, Chem.rdMolDescriptors.CalcMolFormula(mol), mol.GetNumAtoms())


if __name__ == "__main__":
    main()
