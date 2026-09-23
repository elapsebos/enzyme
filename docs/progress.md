# Work status

Updated 2026-09-23.

| Work item | Status | Result |
|---|---|---|
| Local Git repository | Ready locally | Initial commit will capture project docs, scripts, three raw mmCIF structures, and provisional coordinate models. No GitHub remote is configured. |
| Structure selection | Candidate selected | 6EQE is the WT scaffold candidate; 5XH3 and 7XTW are ligand-pose references with catalytic Ser-to-Ala mutations. |
| Sequence/structure mapping | Completed for the five PADFL sites | The expected WT residues at Y87, S121, D186, N233, and N246 are present in 6EQE chain A. |
| WT/PADFL coordinates | Preliminary coordinate files generated | Chain-A heavy-atom WT model and PyMOL rotamer-based PADFL model are available; neither is MD-ready. |
| PET3 chemistry | Defined from literature | Neutral 2-HE(MHET)3, C32H30O14, 76 atoms including H; an isolated MMFF94s starting conformer is generated. |
| PET3 pose | Candidate seed generated, gate still open | HEMT-aligned seed has plausible Ser160/oxyanion-hole distances but a 1.280 Å local fit RMSD and one heavy-atom pair at 2.090 Å. Review and restrained relaxation are still required. |
| GAFF/RESP topology | Not available yet | AmberTools/Antechamber and Gaussian are not installed in this environment. |
| Protonation and solvent preparation | Not available yet | PROPKA, PDBFixer, OpenMM/GROMACS, and force-field tools are not installed. |
| GitHub remote | Not configured | GitHub CLI and a GitHub repository connector are unavailable here; no credentials or remote URL are configured. |

## Immediate next gate

Review CP3 pose geometry and resolve the close contact, then use a supported force-field workflow for protonation, ligand parameterization, restrained minimization, and solvent equilibration. Keep Funnel-MetaD on hold until CP1–CP6 evidence is complete.
