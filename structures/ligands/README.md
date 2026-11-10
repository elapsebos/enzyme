# Ligand files for QM/RESP and pose references

These folders distinguish experimentally observed ligand coordinates from ideal chemical-component structures and QM starting geometries. MOL2 files named `*_zero_placeholder*` or described as zero-placeholder-charge inputs carry no RESP charges and are not production force-field topologies. Set the molecular charge and multiplicity explicitly in the QM input.

| Ligand | Role | QM charge / multiplicity | When RESP is needed |
|---|---|---:|---|
| PET3, 2-HE(MHET)3 | Current production ligand | 0 / 1 | Yes, before MM/Funnel-MetaD and for the MM environment in QM/MM |
| HEMT, CCD 856 | Experimental crystal ligand and proposed MetaD method pilot | 0 / 1 | Yes if used in explicit MM simulation; not needed merely to inspect its crystal pose |
| MHET, CCD C9C neutral | Experimental crystal ligand/pose reference | 0 / 1 as CCD model | No if used only for pose checks; if simulated, choose the protonation state for the target pH first |
| MHET monoanion | Possible aqueous-pH simulation state | -1 / 1 | Yes only if the anionic state is selected for simulation |
| PET4 | Optional chain-length comparison | 0 / 1 in current neutral capped model | Defer unless PET4 is actually included in a simulation |

For HEMT and MHET, `*_crystal_pose.pdb` contains heavy atoms extracted from the experimental complex and is for pose reference. The ideal SDF files have bond orders and hydrogens and are intended to seed QM geometry optimization. QM-start MOL2 files use zero placeholder atom charges; they are not RESP results. The crystal pose and the isolated QM charge-optimization geometry are separate files and serve different purposes.
