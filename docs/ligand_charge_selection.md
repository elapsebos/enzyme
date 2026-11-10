# Ligands to parameterize with RESP

Updated 2026-11-11.

RESP is needed for a ligand when that ligand will be represented in the MM environment of a simulation. It is not needed just to view an experimental pose or measure its geometry.

## Current recommendation

1. **PET3 is required.** It is the selected ligand for the current WT/PADFL Funnel-MetaD project and will remain in the MM environment for QM/MM. Use the neutral 2-HE(MHET)3 structure (net QM charge 0, singlet) already specified in `pet3_definition.md`.
2. **HEMT is recommended if the planned monomer pilot will actually be simulated.** HEMT is the co-crystallized ligand in 5XH3 (component 856), and is a neutral ester model (net QM charge 0, singlet). If it is used only as a visual/structural reference, no RESP calculation is necessary.
3. **MHET is optional.** C9C in 7XTW is the experimental MHET ligand. Keep it as a pose reference without RESP if no MHET simulation is planned. If it is simulated near aqueous neutral pH, evaluate the carboxylate monoanion (net QM charge -1, singlet); the neutral CCD form (0, singlet) is retained separately as the crystal-component chemical reference. Do not calculate or use one state as a substitute for the other.
4. **PET4 is deferred.** It is not part of the current primary system; calculate its RESP charges only if it is added as a chain-length sensitivity system.

## Added structures

`structures/ligands/HEMT_856/` contains the RCSB ideal CCD SDF, the experimental 5XH3 ligand pose, and a neutral QM-start MOL2.

`structures/ligands/MHET_C9C/` contains the RCSB ideal CCD SDF, the experimental 7XTW ligand pose, a neutral CCD-state QM-start MOL2, and a modeled anion SDF/MOL2 candidate.

The MOL2 inputs are geometry/connectivity starts. Their atom charges were explicitly zeroed as placeholders to prevent accidental use of Open Babel Gasteiger charges. Always set the formal molecular charge and multiplicity explicitly in Gaussian/ORCA. Run the selected geometry optimization and ESP/RESP workflow, then return the optimized geometry, ESP/RESP data, logs, and (if available) GAFF/GAFF2-typed, RESP-charged MOL2. The older `structures/PET3/2-HE-MHET3_GASTEIGER_NOT_RESP.mol2` is retained only to make its status explicit; do not submit or use it as RESP input.

The experimental ligand-coordinate PDBs are heavy-atom pose references, not QM charge-optimization geometries. Transfer resulting charges to simulation coordinates only through an explicit atom-name/index mapping.
