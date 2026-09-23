# Candidate IsPETase structures

Downloaded from RCSB PDB on 2026-09-23 as original mmCIF files. The local sequence/coordinate audit is reproducible with scripts/audit_structures.py.

| PDB | Chain A construct | Ligand | Resolution | Local chain residues | Use |
|---|---|---|---:|---:|---|
| 6EQE | Wild type | None | 0.92 Å | 265 (author numbers 29–293) | Primary scaffold candidate |
| 5XH3 | R103G/S131A | HEMT, component 856 | 1.30 Å | 261 (author numbers 1–261) | Active-site pose reference |
| 7XTW | R132G/S160A | C9C, MHET-like | 1.91 Å | 261 (author numbers 30–290) | Experimental MHET pose validation |

## Sequence and coordinate mapping

BioPython global sequence alignment maps 261 C-alpha atoms from each ligand-bound structure onto 6EQE chain A:

- 5XH3 to 6EQE: 0.198 Å C-alpha RMSD; R103G and S131A map to R132G and S160A in 6EQE numbering.
- 7XTW to 6EQE: 0.199 Å C-alpha RMSD; R132G and S160A retain those author numbers.

Both ligand-bound structures replace the catalytic serine with alanine. Use their ligand poses as geometric references, not as final WT/PADFL protein scaffolds.

The five PADFL positions from Zhang et al. (2026; DOI 10.1016/j.biortech.2026.135499) are present in 6EQE chain A with the expected WT identities: Y87, S121, D186, N233, and N246. The position mapping is recorded in mutation_mapping.csv.

## Structural records

- [RCSB 6EQE](https://www.rcsb.org/structure/6EQE): wild-type IsPETase, 0.92 Å, X-ray diffraction.
- [RCSB 5XH3](https://www.rcsb.org/structure/5XH3): R103G/S131A variant with HEMT, 1.30 Å.
- [RCSB 7XTW](https://www.rcsb.org/structure/7XTW): IsPETase in complex with MHET, 1.91 Å; the modeled ligand is component C9C.

## Selection

Use 6EQE as the WT/PADFL scaffold candidate because the deposited construct is WT and the resolution is 0.92 Å. Keep 5XH3 and 7XTW as pose and validation references. This selection still needs review of alternate conformations, unresolved residues, local active-site geometry, and the PADFL paper's exact sequence numbering convention before simulation preparation is frozen.
