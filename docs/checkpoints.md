# Pre-production checkpoints

Advance only when the gate evidence is recorded. A failed gate returns the work to the relevant preparation step.

| Gate | Question | Required evidence | Suggested record |
|---|---|---|---|
| CP0 — System definition | Are the comparison and modeled substrate defined? | WT/PADFL sequence source; candidate scaffold; PET3 chemistry and termini; intended temperature/pH; force-field plan; source records for structural templates | project_definition.md, structure inventory |
| CP1 — Protein preparation | Are WT and PADFL models correct and comparable? | Mutation mapping; chain/residue numbering; missing atoms/residues and alternate locations reviewed; disulfides and catalytic residues checked; protonation/tautomers documented | mutation map, protonation table, prepared structure QC |
| CP2 — PET3 parameters | Is the ligand chemically and mechanically sound? | Exact structure/terminal groups; atom naming; net charge; parameter files; parameterization provenance; geometry and isolated-ligand checks | ligand structure, parameter files, parameterization notes |
| CP3 — Initial complexes | Are the starting complexes justified and comparable? | Placement method recorded; same PET3 reference pose used for WT/PADFL; scissile ester and catalytic geometry checked; clashes reviewed; alternatives documented | complex structures and pose QC |
| CP4 — Solvation/equilibration | Are solvated systems stable? | Water/ion composition and box recorded; minimization and staged equilibration completed; temperature, pressure, density, and structural checks reviewed | inputs, lightweight QC report |
| CP5 — Unbiased MD validation | Does each model behave plausibly before enhanced sampling? | Replicas/design recorded; protein stability, PET orientation/torsions, catalytic distances and hydrogen bonds, and local mutation regions reviewed | pilot inputs and analysis summary |
| CP6 — Funnel-MetaD pilot | Does this system-specific setup work as intended? | CV and funnel definitions reviewed; short pilot verifies bias/output, restart, walker exchange/sharing if used, and accessible bound/unbound regions | pilot input, logs, QC summary |
| CP7 — Production readiness | Are inputs frozen and runs reproducible? | WT/PADFL protocols matched; independent replicas/seeds defined; storage and restart plan; software versions; manifests complete; reviewed commit tagged | run manifests and release tag |

## Mapping from the original backlog

The existing doc/TODO.md remains the detailed working backlog. Structure search, mutation mapping, and PET3 design belong mainly to CP0; protein preparation to CP1; solvation and minimization to CP4; classical MD to CP5; data-driven sampling and Funnel-MetaD design/pilots to CP6; QM/MM is a later project phase after production sampling and representative-state selection.
