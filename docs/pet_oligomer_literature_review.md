# PET oligomer choices in recent PETase simulation studies

Updated 2026-09-23. This note compares ligand choices reported in computational studies and recommends a working substrate for the IsPETase/PADFL Funnel-MetaD and QM/MM project.

## First fix the naming

PET oligomer names are not fully consistent across papers. Some count terephthalate (aromatic) units, while others use expressions such as `2-HE(MHET)n`. In this project, `PET3` and `PET4` mean three or four terephthalate aromatic units, respectively. The working neutral capped structures are `2-HE(MHET)3` (C32H30O14) and `2-HE(MHET)4` (C42H38O18). Record the exact SMILES, end groups, scissile ester, and atom mapping alongside any result; do not rely on the short name alone.

## Examples from the literature

| Study | Substrate used | Why it was selected / role | Implication here |
|---|---|---|---|
| Computational Insights into the Catalytic Mechanism of Is-PETase (Chem. Eur. J., 2022; DOI 10.1002/chem.202201728) | Docking compared HEMT, 2PET, and 3PET; the QM/MM reaction path was then computed for HEMT | HEMT is a small, experimentally anchored local reaction model; longer ligands were used to examine how aromatic contacts and W156 affect pose | Good precedent for separating binding-pose context from a smaller reactive QM model; the QM/MM result itself is not a long-chain substrate calculation |
| Atomistic insight into the binding mode and self-regulation mechanism (PCCP, 2023; DOI 10.1039/D3CP01700A) | Multiple polymerization degrees | To test how IsPETase accommodates different chain lengths across head, middle, and tail binding regions | Supports testing chain-length dependence rather than assuming one oligomer captures all binding behavior |
| Insights into the Enhancement of PET Degradation by FAST-PETase (JACS, 2023; DOI 10.1021/jacs.3c04427) | `2-HE(MHET)3`, explicitly defined as a capped three-unit model in the paper | A chemically defined oligomer suitable for comparing enzyme–substrate interactions; the model was parameterized with RESP/GAFF | Strong reproducible PET3 model, including terminal chemistry and a documented parameterization route |
| Rate-enhancing PETase mutations determined through DFT/MM MD (New J. Chem., 2024; DOI 10.1039/D3NJ04204A) | PET dimer in the QM region (142 QM atoms including selected active-site residues) | The dimer represents the reacting ester environment while keeping the hybrid QM/MM region tractable for comparing variants | Direct precedent for localizing the QM region around a dimeric substrate fragment plus catalytic residues |
| The reaction mechanism of the Ideonella sakaiensis PETase enzyme (Commun. Chem., 2024; DOI 10.1038/s42004-024-01154-x) | Began with a hydroxyethyl-capped PET tetramer, then removed the two units farthest from the active site to use a capped dimer in QM/MM | Retained a polymer-like starting context, then reduced the substrate model for the expensive reactive calculation | A useful multiscale precedent: longer context for binding, smaller local substrate for QM/MM |
| Molecular-Level Mechanistic Insights into PETase-Catalyzed Plastics Hydrolysis (ACS Catal., 2025; DOI 10.1021/acscatal.5c01263) | PET4 and PEF4 | Studied accurate QM/MM free-energy profiles while retaining several repeat units; configurations came from equilibrated polymer–enzyme complexes | Shows that four-unit substrates are practical in advanced QM/MM free-energy work, though the reactive QM region need not contain the entire chain |
| Molecular dynamics simulations of temperature-dependent PET binding (2026) | PET dimer | Authors explicitly chose the smallest oligomer retaining one scissile ester and the local PETase contacts, to compare binding across enzymes and temperatures | A dimer is efficient for local binding comparisons, but gives less chain-contact context for a binding/unbinding collective variable |
| PADFL rational-design study (Bioresour. Technol., 2026; DOI 10.1016/j.biortech.2026.135499) | The project’s local copy reports construction and docking of 4PET | This is the closest precedent because the target enzyme variant is PADFL; reproduce its oligomer size and method where the full methods/supporting files allow | Favors PET4 if the goal is exact PADFL-paper reproduction; exact end-group/coordinate verification remains open |

## Literature-based trade-off and current project choice

From the literature alone, PET4 has a strong case as a production ligand: it matches the PADFL study's reported 4PET choice and retains more chain context for binding-groove interactions. PET3 has a strong case as a well-defined, reproducible model: the FAST-PETase study specifies `2-HE(MHET)3`, including terminal chemistry and a parameterization route.

The current project decision is to use PET3 as the primary ligand for Funnel-MetaD, as directed by the project owner. PET4 is an optional later chain-length sensitivity comparison. Keep this project choice distinct from the literature trade-off; it does not claim PET3 is universally more representative than PET4.

For reaction free energies, do not put the entire PET3 ligand in the QM region by default. Keep PET3 in the full enzyme–substrate model, but use a chemically complete local QM region around the scissile ester, catalytic Ser/His/Asp residues, oxyanion-hole donors, and any directly coupled water/proton-transfer species. Test whether the energy profile changes when the QM region is enlarged to include the adjacent repeat. A later PET3/PET4 comparison on representative snapshots can measure whether the extra repeat units affect the local barrier or mainly binding/pose stability.

The present PET3 coordinates are only a rough HEMT-derived placement seed. They have no heavy-atom pairs below 2.0 Å, but one pair is at 2.090 Å; the pose still needs review and restrained relaxation before use. The separate PET4 seed has substantial clashes and is not suitable for simulation. Neither seed is MD-ready.

## Sources

- Chen et al., PCCP 2023, DOI 10.1039/D3CP01700A.
- García-Meseguer et al., JACS 2023, DOI 10.1021/jacs.3c04427.
- RSC, New J. Chem. 2024, DOI 10.1039/D3NJ04204A.
- Chem. Eur. J. 2022, DOI 10.1002/chem.202201728.
- Commun. Chem. 2024, DOI 10.1038/s42004-024-01154-x.
- ACS Catal. 2025, DOI 10.1021/acscatal.5c01263.
- Bioresour. Technol. 2026, DOI 10.1016/j.biortech.2026.135499.
