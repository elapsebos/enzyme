#!/usr/bin/env python
"""Sequence-map candidate IsPETase mmCIF structures and report C-alpha RMSD."""
from pathlib import Path
import hashlib

from Bio import Align
from Bio.PDB import MMCIF2Dict, MMCIFParser
from Bio.PDB.Superimposer import Superimposer
from Bio.SeqUtils import seq1


ROOT = Path(__file__).resolve().parents[1]
FILES = [ROOT / "structures" / "raw" / f"{pdb}.cif" for pdb in ("6EQE", "5XH3", "7XTW")]


def protein_chain(path, chain_id="A"):
    structure = MMCIFParser(QUIET=True).get_structure(path.stem, str(path))
    chain = structure[0][chain_id]
    residues = [r for r in chain if r.id[0] == " " and seq1(r.resname, custom_map={"UNK": "X"})]
    residues = [r for r in residues if seq1(r.resname, custom_map={"UNK": "X"}) != "X"]
    sequence = "".join(seq1(r.resname) for r in residues)
    return chain, residues, sequence


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def resolution(path):
    data = MMCIF2Dict.MMCIF2Dict(str(path))
    value = data.get("_refine.ls_d_res_high", ["?"])[0]
    return value.strip("'\"")


def main():
    records = {p.stem: (p, *protein_chain(p)) for p in FILES}
    reference = records["6EQE"][3]
    aligner = Align.PairwiseAligner()
    aligner.mode = "global"
    aligner.match_score = 2
    aligner.mismatch_score = -1
    aligner.open_gap_score = -5
    aligner.extend_gap_score = -0.5

    ref_chain, ref_residues, _ = records["6EQE"][1:]
    print("pdb\tchain\tresidues\tauthor_range\tresolution_A\tsha256")
    for pdb, (path, chain, residues, sequence) in records.items():
        print(f"{pdb}\tA\t{len(residues)}\t{residues[0].id[1]}-{residues[-1].id[1]}\t{resolution(path)}\t{sha256(path)}")

    for pdb in ("5XH3", "7XTW"):
        path, chain, residues, sequence = records[pdb]
        alignment = aligner.align(reference, sequence)[0]
        ref_atoms, mob_atoms, differences = [], [], []
        for (ra, rb), (qa, qb) in zip(*alignment.aligned):
            for i, j in zip(range(ra, rb), range(qa, qb)):
                if reference[i] != sequence[j]:
                    differences.append(
                        f"{reference[i]}{ref_residues[i].id[1]}{sequence[j]}(chain-index {i+1}->{j+1})"
                    )
                if "CA" in ref_residues[i] and "CA" in residues[j]:
                    ref_atoms.append(ref_residues[i]["CA"])
                    mob_atoms.append(residues[j]["CA"])
        superimposer = Superimposer()
        superimposer.set_atoms(ref_atoms, mob_atoms)
        print(f"{pdb} vs 6EQE: aligned_CA={len(ref_atoms)} RMSD_A={superimposer.rms:.3f} differences={','.join(differences) or 'none'}")


if __name__ == "__main__":
    main()
