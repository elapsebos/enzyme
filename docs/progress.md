# Work status

Updated 2026-11-11. Input readiness is detailed in md_input_readiness.md.

| Work item | Status | Result |
|---|---|---|
| Local Git repository | Ready locally | Initial commit captures project docs, scripts, three raw mmCIF structures, and provisional coordinate models. No GitHub remote is configured. |
| Structure selection | Candidate selected | 6EQE is the WT scaffold candidate; 5XH3 and 7XTW are ligand-pose references with catalytic Ser-to-Ala mutations. |
| Sequence/structure mapping | Completed for the five PADFL sites | The expected WT residues at Y87, S121, D186, N233, and N246 are present in 6EQE chain A. |
| WT/PADFL coordinates | Preliminary coordinate files generated | Chain-A heavy-atom WT model and PyMOL rotamer-based PADFL model are available; neither is MD-ready. |
| PET3 chemistry | Defined from literature | Neutral 2-HE(MHET)3, C32H30O14, 76 atoms including H; an isolated MMFF94s starting conformer is generated. |
| PET3 pose | Candidate seed generated; CP3 not passed | HEMT-aligned seed has plausible Ser160/oxyanion-hole distances, 1.280 Å local fit RMSD, no heavy-atom pair below 2.0 Å, and one pair at 2.090 Å. It still needs restrained relaxation, geometry review, and matched WT/PADFL pose validation. |
| PET4 chemistry and pose | Provisional model generated; gate failed | 2-HE(MHET)4, C42H38O18, 98 atoms including H, is a working reconstruction of the four-unit ligand reported for PADFL. Current HEMT-derived seed has four protein–ligand heavy-atom pairs below 2.0 Å (minimum 1.566 Å); regenerate or dock and relax it before use. Exact source terminal chemistry still needs confirmation. |
| Project ligand choice | PET3 primary; PET4 optional comparison | Current project decision is to use literature-defined 2-HE(MHET)3 as the primary ligand. PET4 remains available for a later chain-length sensitivity study. See pet_oligomer_literature_review.md and decisions.md. |
| GAFF/RESP topology | Workflow configured; final parameters not available | The fir workflow now selects ORCA gas-phase HF/6-31G* + Multiwfn RESP. Module prerequisites and Slurm account/partition still need confirmation. No actual QM results have been returned; no production ligand topology is frozen. |
| Protonation and solvent preparation | Not completed for the project WT/PADFL | The two preliminary protein PDBs still contain zero hydrogens. The protonation table is pending; Maestro preparation outputs have not replaced these candidates. |
| Published author systems | Downloaded and indexed; project validation pending | Four studies provide parameterized/solvated systems or GROMACS run inputs. These differ in ligand, force field, and reaction state and are not matched WT/PADFL–PET3 inputs. See structures/published/README.md and md_input_readiness.md. |
| GitHub remote | Not configured | GitHub CLI and a GitHub repository connector are unavailable here; no credentials or remote URL are configured. |

## Immediate next gate

Complete CP1 protein preparation and CP2 PET3 GAFF/RESP parameterization. Then refine the PET3 pose, validate the same reference pose in WT and PADFL, and proceed to solvation/equilibration. Keep Funnel-MetaD on hold until CP1–CP6 evidence is complete.
