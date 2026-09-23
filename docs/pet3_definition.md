# PET3 model definition

## Literature target

Use the substrate definition in García-Meseguer et al., “Insights into the Enhancement of the Poly(ethylene terephthalate) Degradation by FAST-PETase from Computational Modeling,” JACS 2023, DOI: 10.1021/jacs.3c04427. The paper calls the model 2-HE(MHET)3: 2-hydroxyethyl-(mono-hydroxyethyl terephthalate)3.

The molecular structure shown in Scheme 2 is a three-terephthalate oligomer with four ethylene-glycol segments and hydroxyl termini. The neutral whole-ligand formula is C32H30O14, with 76 atoms including hydrogens. The chosen SMILES is recorded in scripts/build_pet3.py and is checked against this formula and atom count.

## Preparation status

- A single gas-phase starting conformer may be generated with RDKit MMFF for coordinate preparation only.
- The paper parameterized the ligand with GAFF and RESP charges from HF/6-31G(d); those parameters have not yet been generated here.
- The 5XH3 HEMT pose is the intended active-site anchor. A final aligned pose and scissile-ester choice still require explicit atom mapping and geometry review.
- Do not use the RDKit MMFF conformer or Gasteiger charges as a production MD topology.

## Reproducibility

Record the selected conformer seed, RDKit version, output checksum, atom names/index map, charge, and AmberTools/Gaussian versions when parameterization is performed.
