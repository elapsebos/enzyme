# PET3 QM/RESP handoff

## Input

- `structures/PET3/2-HE-MHET3_qm_start_neutral_ZERO_PLACEHOLDER.mol2`
- 2-HE(MHET)3, C32H30O14, 76 atoms including explicit hydrogens, 78 bonds.
- Neutral molecule: set total charge to 0 and multiplicity to 1.
- The coordinates are the isolated RDKit MMFF94s starting conformer. MOL2 atom charges are all zero placeholders. They must not be read as RESP charges or used in a production MM topology.

## Requested calculation

Use the literature-compatible HF/6-31G(d) route for a geometry optimization followed by an electrostatic-potential calculation and RESP fitting. Keep the total molecular charge neutral and preserve the atom order/names or provide an explicit atom-mapping table if the QM software reorders atoms. ORCA is acceptable if the existing workflow produces a suitable ESP dataset and a documented RESP fit; CHELPG, Mulliken, or Gasteiger charges are not interchangeable with RESP without an explicit project decision.

## Return files

1. Final optimized coordinates in MOL2/SDF/XYZ, with atom order mapped to the input.
2. The QM output/log and the ESP data or grid used for fitting.
3. A RESP-charged MOL2 with GAFF/GAFF2 atom types if the submitted workflow also parameterizes the ligand.
4. A short calculation record: software/version, method/basis, charge/multiplicity, convergence status, conformer/geometry used, RESP settings, net fitted charge, and any restraints or symmetry constraints.

If the existing script only accepts MOL2 as geometry input, the zero-placeholder file is suitable as that input. If it requires pre-existing RESP charges or GAFF types, the script's input specification is needed before generating a final topology file.

## Protein protonation status

No protonation calculation has been performed. The current WT/PADFL files contain heavy atoms only; no hydrogens or histidine tautomers have been assigned. Record the target simulation pH first, then estimate pKa values for WT and PADFL separately and inspect catalytic Asp206/His237/Ser160, active-site hydrogen bonds, buried titratable residues, and any mutation-adjacent sites. Use a matched protocol for WT and PADFL and document any state differences. For the catalytic His, explicitly compare the neutral tautomer consistent with the Asp206–His237–Ser160 hydrogen-bond network; do not assign it from residue name alone.
