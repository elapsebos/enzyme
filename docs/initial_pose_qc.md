# PET3 initial-pose seed QC

This is an initial geometric seed, not a relaxed enzyme-substrate complex or an MD-ready input.

- Ligand: literature 2-HE(MHET)3; C32H30O14; 76 atoms including hydrogens.
- Alignment template: HEMT component 856 in 5XH3 chain A.
- Mapped PET3 central terephthalate unit onto the HEMT aromatic ring and ester groups.
- HEMT atoms used: C05, C06, C07, C08, C15, C16, C03, O04, O02, C01, C09, O10, O11, C12, C13, O14.
- All mapped local HEMT/PET3-fragment fit RMSD: 1.280 Å.
- Central ring/reactive-carbonyl RMSD within that fit: 1.417 Å.
- 5XH3-to-6EQE protein C-alpha alignment RMSD: 0.198 Å.
- Ser160 OG to scissile carbonyl C distance: 2.730 Å.
- Oxyanion carbonyl O to Tyr87 N / Met161 N distances: 3.040 / 2.892 Å.
- Closest ligand/protein heavy-atom distance: 2.090 Å.
- Ligand/protein heavy-atom pairs under 2.0 Å: 0; under 2.5 Å: 1.
- The scissile carbonyl in the chosen seed is PET3 atom index 22, oxygen index 23, ester oxygen index 24 (zero-based RDKit atom indices).

Review this pose visually and inspect clashes, torsions, oxyanion-hole geometry, and the Ser160 nucleophile distance before restrained relaxation. The HEMT structure is a catalytically inactive mutant, so this template constrains binding geometry but does not supply a WT catalytic state.
