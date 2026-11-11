# PET4 initial-pose seed QC

This is an initial geometric seed, not a relaxed enzyme-substrate complex or an MD-ready input.

- Ligand: 2-HE(MHET)4; C42H38O18; 98 atoms including hydrogens.
- Alignment template: HEMT component 856 in 5XH3 chain A.
- Mapped the central terephthalate unit of PET4 onto the HEMT aromatic ring and ester groups.
- HEMT atoms used: C05, C06, C07, C08, C15, C16, C03, O04, O02, C01, C09, O10, O11, C12, C13, O14.
- All mapped local HEMT/PET4-fragment fit RMSD: 2.100 Å.
- Central ring/reactive-carbonyl RMSD within that fit: 2.466 Å.
- 5XH3-to-6EQE protein C-alpha alignment RMSD: 0.198 Å.
- Ser160 OG to scissile carbonyl C distance: 2.318 Å.
- Oxyanion carbonyl O to Tyr87 N / Met161 N distances: 2.575 / 3.625 Å.
- Closest ligand/protein heavy-atom distance: 1.566 Å.
- Ligand/protein heavy-atom pairs under 2.0 Å: 4; under 2.5 Å: 13.
- The scissile carbonyl in the chosen seed is PET4 atom index 22, oxygen index 23, ester oxygen index 24 (zero-based RDKit atom indices).

Review this pose visually and inspect clashes, torsions, oxyanion-hole geometry, and the Ser160 nucleophile distance before restrained relaxation. The HEMT structure is a catalytically inactive mutant, so this template constrains binding geometry but does not supply a WT catalytic state.
