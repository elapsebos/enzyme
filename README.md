# IsPETase–PET3 WT/PADFL Project

This repository tracks the structural preparation and simulation workflow for comparing wild-type IsPETase and the PADFL variant with a PET trimer substrate.

## Current status

The project has candidate structures downloaded and sequence-audited. 6EQE is the current WT scaffold candidate; structure preparation, PET3 active-site placement, protonation, and simulation parameters are not frozen.

## Project records

- doc/TODO.md: original working backlog.
- docs/project_definition.md: scope, assumptions, and decisions that need verification.
- docs/checkpoints.md: go/no-go gates before production Funnel-MetaD.
- docs/structure_inventory.csv: structure comparison and selection record.
- docs/mutation_mapping.csv: sequence-to-structure mutation mapping.
- docs/protonation_table.csv: residue-level protonation decisions.
- docs/run_manifest.template.yaml: provenance template for each simulation run.
- docs/structure_comparison.md: verified structure metadata and sequence mapping.
- docs/pet3_definition.md: PET3 literature definition and remaining parameterization work.
- docs/protein_preparation.md: status and limits of the coordinate-only WT/PADFL structures.
- docs/initial_pose_qc.md: current PET3 placement seed and geometric checks.
- docs/progress.md: completed and blocked stages.
- structures/raw/: original mmCIF coordinate files downloaded from RCSB PDB.

## Suggested layout

Keep small inputs, scripts, decisions, and analysis code in version control. The source PDFs and DOCX remain local and are excluded by .gitignore. Keep production trajectories and other large outputs in project storage, with their locations and checksums recorded in run manifests.

    docs/          project decisions, checklists, literature notes, templates
    structures/    source and prepared structures
    preparation/   preparation scripts and reproducible inputs
    forcefield/    ligand parameterization inputs and notes
    mdp/           GROMACS run parameter files
    plumed/        PLUMED inputs and analysis definitions
    analysis/      analysis scripts and small summary outputs
    runs/          per-run manifests and lightweight metadata
    scripts/       reproducible structure and ligand preparation utilities

## Git use

Use main for reviewed, reproducible project states. Create a short-lived branch for a preparation or analysis change, commit the inputs and decision record together, and tag completed gates (for example, cp1-protein-prep). Do not commit trajectories or production output; .gitignore covers common simulation output patterns.

Before starting a production run, record the repository commit, software versions, input files, system identity, and run location in a copy of docs/run_manifest.template.yaml.
