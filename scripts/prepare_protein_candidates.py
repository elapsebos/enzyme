#!/usr/bin/env python
"""Write chain-A heavy-atom WT and provisional PADFL coordinate models."""
from pathlib import Path

from Bio.PDB import MMCIFParser, PDBIO, Select
from Bio.PDB.Polypeptide import is_aa
import pymol2


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "structures" / "raw" / "6EQE.cif"
OUT = ROOT / "structures" / "prepared"
OUT.mkdir(parents=True, exist_ok=True)
WT_OUT = OUT / "6EQE_WT_chainA_heavy.pdb"
PADFL_OUT = OUT / "PADFL_from_6EQE_rotamer_preliminary.pdb"
MUTATIONS = [(87, "PHE"), (121, "PRO"), (186, "ALA"), (233, "LEU"), (246, "ASP")]


class ProteinHeavyAtoms(Select):
    def accept_chain(self, chain):
        return chain.id == "A"

    def accept_residue(self, residue):
        return is_aa(residue, standard=False)

    def accept_atom(self, atom):
        return atom.element not in {"H", "D"}


structure = MMCIFParser(QUIET=True).get_structure("6EQE", str(RAW))
for chain in list(structure[0]):
    if chain.id != "A":
        structure[0].detach_child(chain.id)
for residue in structure.get_residues():
    disordered = [atom for atom in residue.child_list if atom.is_disordered() == 2]
    if not disordered:
        continue
    occupancies = {}
    for atom in disordered:
        for altloc, child in atom.child_dict.items():
            occupancies[altloc] = occupancies.get(altloc, 0.0) + (child.get_occupancy() or 0.0)
    chosen_altloc = max(occupancies, key=occupancies.get)
    for atom in disordered:
        child = atom.child_dict.get(chosen_altloc)
        if child is None:
            child = max(atom.child_dict.values(), key=lambda a: a.get_occupancy() or 0.0)
        residue.detach_child(atom.id)
        child.set_altloc(" ")
        child.disordered_flag = 0
        residue.add(child)
io = PDBIO()
io.set_structure(structure)
io.save(str(WT_OUT), ProteinHeavyAtoms())

pymol = pymol2.PyMOL()
pymol.start()
cmd = pymol.cmd
cmd.load(str(WT_OUT), "PADFL")
cmd.wizard("mutagenesis")
for residue_number, new_resname in MUTATIONS:
    wizard = cmd.get_wizard()
    selection = f"chain A and resi {residue_number}"
    if cmd.count_atoms(selection + " and name CA") != 1:
        raise ValueError(f"Expected one CA at residue {residue_number}")
    wizard.set_mode(new_resname)
    wizard.do_select(selection)
    # PyMOL's mutagenesis wizard selects its lowest-bump rotamer by default.
    wizard.apply()
cmd.set_wizard()
cmd.save(str(PADFL_OUT), "PADFL")
pymol.stop()
print(f"Wrote {WT_OUT}")
print(f"Wrote provisional, unminimized {PADFL_OUT}")
