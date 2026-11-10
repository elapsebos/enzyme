# Protein preparation status

## Candidate outputs

- structures/prepared/6EQE_WT_chainA_heavy.pdb: chain A from 6EQE, protein heavy atoms only, water/ions removed, one highest-occupancy alternate conformer selected per residue.
- structures/prepared/PADFL_from_6EQE_rotamer_preliminary.pdb: the same scaffold with PADFL side-chain substitutions introduced using PyMOL's mutagenesis wizard and its lowest-bump rotamer choice.

The preliminary model contains the expected identities at 87F, 121P, 186A, 233L, and 246D. It is a coordinate model only.

## Not yet prepared for MD

Rechecked on 2026-11-11: the WT file contains 1,952 atoms and PADFL 1,949 atoms; both have 265 residues and zero hydrogen atoms. The five WT/PADFL identities and Ser160/Asp206/His237 identities are present. This confirms residue identities only, not protonation or catalytic readiness. Downloaded author systems are kept separately under structures/published; see docs/md_input_readiness.md for their different preparation states.

Neither file has hydrogens, a frozen protonation/His tautomer assignment, missing-terminal reconstruction, force-field topology, minimization, or solvent/ions. The PADFL side chains have not been energy-minimized against the protein environment. Do not use these files directly for production MD.

## Required next preparation

1. Confirm the PADFL numbering convention against the full sequence in the article/SI and the 6EQE reference sequence.
2. Review altloc choices and any unresolved regions near the active site and the five mutations.
3. Run a consistent protonation workflow for WT and PADFL, then inspect the catalytic triad and mutation-driven pKa changes.
4. Rebuild missing atoms/residues as needed and perform force-field preparation/minimization with a supported protein force field.
5. Record software versions and compare matched WT/PADFL structures before adding PET3.
