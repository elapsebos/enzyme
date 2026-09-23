# Decision log

Record consequential choices here. Keep entries short and link to the evidence or input files that support them. Do not silently replace an earlier decision; add a dated follow-up entry.

| Date | Decision | Alternatives considered | Evidence/source | Status | Follow-up |
|---|---|---|---|---|---|
| 2026-09-23 | Create a tracked project scaffold; keep scientific inputs and assignments explicitly provisional | — | doc/TODO.md and project discussion in doc/核实IsPETase复合结构_2026-09-23 15_26_10.md | current | Verify PDB records, PADFL sequence/mapping, and PET3 chemistry before freezing CP0 |
| 2026-09-23 | Use 6EQE chain A as the WT/PADFL scaffold candidate; retain 5XH3 and 7XTW as ligand-pose references | Use ligand-bound mutant as starting protein | RCSB records and pairwise chain-A sequence/coordinate audit; see structure_comparison.md | draft | Review unresolved regions and active-site geometry before CP1 sign-off |
| 2026-09-23 | Define PET3 as the literature 2-HE(MHET)3 oligomer | Other terminal-group definitions | García-Meseguer et al., JACS 2023, DOI 10.1021/jacs.3c04427; see pet3_definition.md | draft | Confirm atom naming/scissile ester and complete GAFF/RESP parameterization |
| 2026-09-23 | Target PET4 (four terephthalate units) for production Funnel-MetaD; retain PET3 as a benchmark | PET3 alone; longer oligomers | PADFL 2026 paper reports 4PET; recent PETase binding/QM/MM studies use oligomers from dimers to tetramers; see pet_oligomer_literature_review.md | superseded by the next entry | Keep as a record of the literature-based option; use PET3 per the current project decision |
| 2026-09-23 | Use literature-defined PET3 (2-HE(MHET)3) as the primary ligand for the current Funnel-MetaD project; keep PET4 as an optional length comparison | PET4 as primary | Project owner direction; PET3 chemical definition and literature precedent are recorded in pet3_definition.md and pet_oligomer_literature_review.md | current | Finish protein preparation and PET3 GAFF/RESP parameters, then refine and validate the matched WT/PADFL pose |
| 2026-09-23 | Generate a provisional PADFL coordinate model using the 6EQE scaffold and PyMOL's lowest-bump side-chain rotamers | — | prepare_protein_candidates.py and protein_preparation.md | provisional | Rebuild/relax under the selected force field and verify side-chain states |
