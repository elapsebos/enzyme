# Project definition (draft)

## Research objective

Compare wild-type IsPETase and the PADFL variant with a modeled PET oligomer, then assess whether their bound and catalytic-ready conformational ensembles differ. PET4 (four terephthalate units) is the intended production ligand for Funnel-MetaD; PET3 is a lower-cost benchmark. QM/MM calculations should initially focus on the reacting ester and its local catalytic environment, with PET4 retained in the MM context unless convergence tests support a larger QM region.

## Draft workflow

1. Select and document the protein starting structure(s).
2. Map the PADFL sequence and mutations onto the chosen structure; prepare matched WT and variant models.
3. Define PET3/PET4 chemical identity, terminal groups, atom names, and parameterization route.
4. Construct a common, experimentally informed oligomer reference pose, using the HEMT pose in 5XH3 as a candidate anchor and MHET-bound structures as a validation reference where appropriate.
5. Solvate, add ions, minimize, equilibrate, and validate with unbiased MD.
6. Validate the CVs, funnel geometry, restart behavior, and replica/walker setup in a short Funnel-MetaD pilot.
7. Freeze inputs and provenance before production sampling.

## Working structural references (unverified selection)

| Structure | Intended use | Status / caveat |
|---|---|---|
| 6EQE | Candidate WT scaffold | Confirm chain, construct, missing regions, and suitability before selection. |
| 5XH3 | HEMT-bound active-site geometry reference | Confirm ligand atoms, chain/residue numbering, and mutation state from the primary record. |
| 7XTW | MHET-bound pose validation | Confirm ligand identity and construct mutations from the primary record. |

These are candidates described in the project notes, not yet verified project inputs. Record sources and download dates in structure_inventory.csv before use.

## Open decisions

- Confirm the PADFL sequence and exact mutation set, then map every mutation to the selected structure numbering.
- Select a primary protein structure and document why it is suitable.
- Verify PET4 terminal chemistry against the PADFL paper's model files or supporting information; retain the documented PET3 as a benchmark. Record protonation/charge and the scissile ester for both.
- Decide how PET3 is placed and which ester is treated as the initial scissile bond.
- Freeze protonation and tautomer assignments consistently for WT and PADFL, with explicit catalytic-triad inspection.
- Select and record protein, ligand, water, and ion force-field models and software versions.
- Confirm the production sampling design only after the pilot gates pass.

## Evidence and uncertainty policy

Do not treat residue numbers or claims copied from discussion notes as verified. Use the sequence, coordinate file, and primary structure/publication records to resolve numbering and chemistry. Record each decision, evidence source, date, and reviewer in the relevant project table or a dated entry in docs/decisions.md.
