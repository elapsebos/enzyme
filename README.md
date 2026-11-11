# IsPETase–PET3 WT/PADFL Project

Version: **[0.1.0](VERSION)** · Updated: **2026-11-12**

This repository contains structure candidates, ligand models, preparation scripts, and research records for comparing wild-type IsPETase with the PADFL variant using PET3, `2-HE(MHET)3`. The planned workflow combines unbiased molecular dynamics (MD), funnel metadynamics (Funnel-MetaD), and subsequent QM/MM analysis of selected catalytic states. PET4 is retained as an optional chain-length comparison.

**The project is in the input-preparation stage. Validated WT–PET3 and PADFL–PET3 production systems are not yet available.**

## Current state

| Component | Available files and status |
| --- | --- |
| Protein references | Original RCSB mmCIF files for 6EQE, 5XH3, and 7XTW. 6EQE is the WT scaffold candidate; the ligand-bound structures provide pose references. |
| WT and PADFL models | Preliminary chain-A heavy-atom coordinates derived from 6EQE. PADFL carries Y87F/S121P/D186A/N233L/N246D in the working 6EQE numbering. Protein protonation, local refinement, and topology preparation remain pending. |
| PET3 | Neutral `2-HE(MHET)3`, C32H30O14, with 76 atoms including hydrogens. An isolated MMFF94s conformer, QM input, and HEMT-aligned pose seed are available. The pose still needs relaxation and validation in both proteins. |
| PET4 | Provisional neutral `2-HE(MHET)4`, C42H38O18, with 98 atoms including hydrogens. Its current pose seed has severe clashes; terminal chemistry and placement require further review. |
| Ligand charges | A configurable RESP/RESP2 Slurm workflow is available. The current configuration selects ORCA gas-phase HF/6-31G* with Multiwfn RESP; final project RESP charges and GAFF/GAFF2 parameters are pending. |
| Published systems | Provenance and inventories for four published simulation datasets are tracked. Downloaded archives and extracted author files remain local. Their chemistry, reaction states, and force fields differ from the project WT/PADFL–PET3 comparison. |
| MD and enhanced sampling | Project solvation, equilibration, unbiased MD validation, and Funnel-MetaD pilots remain pending. |

See [MD input readiness](docs/md_input_readiness.md) for the detailed assessment and [checkpoints](docs/checkpoints.md) for the evidence required before production sampling.

## Repository layout

The tree below shows the current project layout. Local caches and temporary files are omitted.

```text
enzyme/
├── README.md
├── VERSION
├── docs/                            # Decisions, QC, literature notes, and provenance tables
├── scripts/                         # Structure audits, ligand construction, and archive utilities
├── ligprep/
│   ├── README.md                    # Detailed charge-workflow instructions
│   ├── config.json                  # Current ORCA + Multiwfn RESP configuration
│   ├── config.example.json          # ORCA + Multiwfn RESP example
│   ├── config.gaussian-resp.example.json
│   ├── config.resp2.example.json
│   ├── run.sh                       # Job-preparation entry point
│   ├── input/                       # Explicit-hydrogen HEMT and PET3 MOL2 inputs
│   ├── scripts/                     # Pipeline implementation and mock tests
│   ├── output/                      # Local generated jobs and calculation results
│   └── legacy/                      # Archived workflows retained for reference
└── structures/
    ├── raw/                         # Original 6EQE, 5XH3, and 7XTW mmCIF files
    ├── prepared/                    # Preliminary WT and PADFL protein coordinates
    ├── PET3/                        # PET3 identity, conformer, pose seed, and QM input
    ├── PET4/                        # Provisional PET4 conformer and pose seed
    ├── ligands/
    │   ├── HEMT_856/                # Experimental HEMT pose and QM starting geometry
    │   └── MHET_C9C/                # Experimental C9C pose and neutral/anion models
    └── published/                   # Author-system provenance and structure inventories
        ├── jerves_2021_RESP_PET2/
        ├── burgin_2024_CGenFF_PET2/
        ├── berselli_2025_AM1BCC_PET4_PEF4/
        └── dipede_2026_RESP_PET4/
```

Generated `ligprep/output/` contents are ignored except for `.gitkeep`. Within each published-source directory, `archives/`, `extracted/`, and `derived/` are local-only directories and are not included in a Git clone. Their provenance records and inventories are tracked.

## Getting started

```bash
git clone https://github.com/elapsebos/enzyme.git
cd enzyme
```

Start with the [project definition](docs/project_definition.md), [structure comparison](docs/structure_comparison.md), and [MD input readiness](docs/md_input_readiness.md). The existing coordinate files can be inspected without regenerating them.

### Requirements

Dependencies vary by task; the repository does not currently provide a pinned environment or a package installer.

| Task | Requirements |
| --- | --- |
| Ligand job preparation and local mock tests | Python 3.10+; Python standard library only. Bash is needed for `run.sh`. |
| Structure sequence/coordinate audit | Biopython and its dependencies. |
| PET3/PET4 conformer construction | RDKit. |
| Ligand pose placement | NumPy, Biopython, and RDKit. |
| Reference-ligand extraction | Biopython and RDKit; the tracked ideal SDF files must be present. |
| WT/PADFL coordinate regeneration | Biopython and a PyMOL installation exposing `pymol2`. |
| Published archive download/indexing | `requests`, including for the indexer through its downloader import; local archives are required for offline indexing. |
| Actual charge calculations | Slurm and the selected QM/fitting programs. The current route requires `orca`, `orca_2mkl`, and `Multiwfn`. |

For fir, follow the [environment policy](docs/fir_environment_policy.md) and [ORCA RESP checklist](docs/orca_resp_fir_checklist.md). The charge workflow uses platform modules and rejects an active Conda environment by default. Candidate module versions still need their dependencies checked on fir.

### Inspect structures and check the charge pipeline

Run these commands from the repository root:

```bash
# Report source-file checksums, residue mapping, and C-alpha alignment RMSDs.
python3 scripts/audit_structures.py

# Run local tests using simulated QM and fitting outputs.
python3 ligprep/scripts/test_pipeline.py -v
```

The mock tests do not require Slurm or QM software and do not validate a real calculation on fir.

### Prepare ligand charge jobs

1. Review [the input notes](ligprep/input/README.md) and [the full workflow guide](ligprep/README.md).
2. Edit `ligprep/config.json`: set the Slurm account and partition, verify module dependencies and program paths, and review resources, charge, multiplicity, and ligand selection. The account and partition are currently `null`, so the configuration must be completed before jobs can be prepared.
3. Keep `execution.submit=false` to generate jobs for inspection. The current configuration enables HEMT and disables PET3 for the initial environment check.

```bash
# Generate a new batch after completing the configuration.
bash ligprep/run.sh

# Submit a reviewed job from its generated output directory.
sbatch job.sbatch
```

Each preparation run creates a new batch. Run `sbatch job.sbatch` inside the selected generated job directory after reviewing its contents. With a validated configuration, `bash ligprep/run.sh --submit` prepares and submits a new batch directly.

Jobs retain input/configuration snapshots, calculation logs, fitted charges, and status records. `result_RESP.mol2` or `result_RESP2.mol2` contains fitted charges on the original input geometry; it still requires force-field typing and parameter preparation before use as a complete MD ligand model.

## Structure and dataset utilities

These commands are available for deliberate regeneration or data retrieval. Except for the audit, they write project files and may replace existing generated structures, QC reports, or inventories. Review local changes before running them.

| Command | Purpose and prerequisites |
| --- | --- |
| `python3 scripts/audit_structures.py` | Read the three raw mmCIF files and print sequence mapping, checksums, and protein alignment statistics. |
| `python3 scripts/prepare_protein_candidates.py` | Generate the heavy-atom WT model and the preliminary PyMOL rotamer-based PADFL model from 6EQE. |
| `python3 scripts/build_pet3.py` | Rebuild the isolated PET3 MMFF94s conformer and SMILES file. |
| `python3 scripts/build_pet4.py` | Rebuild the provisional PET4 MMFF94s conformer and SMILES file. |
| `python3 scripts/place_pet3_on_5xh3.py --units 3` | Generate a HEMT-aligned PET3 pose seed in the 6EQE reference frame and rewrite its QC report; requires the prepared WT PDB. |
| `python3 scripts/place_pet3_on_5xh3.py --units 4` | Generate the corresponding provisional PET4 pose seed and rewrite its QC report; the same WT prerequisite applies. |
| `python3 scripts/extract_reference_ligands.py` | Extract crystal-pose HEMT/C9C coordinates and generate an MHET anion conformer. This does not generate the QM-start MOL2 files. |
| `python3 scripts/download_published_structures.py` | Download and verify the configured Figshare/Zenodo archives for the 2021, 2024, and 2025 studies, then extract selected files and write inventories. Requires network access. |
| `python3 scripts/index_published_structures.py` | Re-extract and index locally available author archives. If the 2026 GitHub snapshot is present, validate its blobs using the recorded commit/tree metadata. |

Shared oligomer definitions, atom mappings, and conformer seeds are maintained in [`scripts/pet3_spec.py`](scripts/pet3_spec.py). The construction scripts produce initial conformers and pose seeds; they do not perform complete force-field parameterization.

For dataset sources, checksums, and reconstruction details, see [published structures](structures/published/README.md). The downloader does not fetch the 2026 GitHub snapshot; its fixed-commit URL is recorded in that dataset's [provenance](structures/published/dipede_2026_RESP_PET4/provenance.json).

## Documentation guide

| Topic | Records |
| --- | --- |
| Scope and decisions | [Project definition](docs/project_definition.md), [decision log](docs/decisions.md), [checkpoints](docs/checkpoints.md) |
| Progress and readiness | [Work status](docs/progress.md), [MD input readiness](docs/md_input_readiness.md). Status entries are dated snapshots; the Git remote is now configured. |
| Protein structures | [Structure comparison](docs/structure_comparison.md), [structure inventory](docs/structure_inventory.csv), [mutation mapping](docs/mutation_mapping.csv), [protein preparation](docs/protein_preparation.md), [protonation table](docs/protonation_table.csv) |
| Ligand identity and pose QC | [PET3 definition](docs/pet3_definition.md), [oligomer literature review](docs/pet_oligomer_literature_review.md), [PET3 pose QC](docs/initial_pose_qc.md), [PET4 pose QC](docs/initial_pose_qc_pet4.md), [reference-ligand guide](structures/ligands/README.md) |
| Charge methods and handoff | [Charge selection](docs/ligand_charge_selection.md), [literature audit](docs/ligand_charge_literature_audit.md), [PET3 QM handoff](docs/pet3_hpc_qm.md), [charge pipeline](ligprep/README.md) |
| fir configuration | [Environment policy](docs/fir_environment_policy.md), [module selection](docs/fir_module_selection.md), [ORCA RESP checklist](docs/orca_resp_fir_checklist.md), [workflow review](docs/fir_ligprep_review.md) |
| Published systems and provenance | [Published dataset guide](structures/published/README.md), [download summary](structures/published/download_summary.json), [structure contents](structures/published/structure_contents.json), [run manifest template](docs/run_manifest.template.yaml) |

## Scientific and reproducibility notes

- Preserve the original files in `structures/raw/`. Keep prepared coordinates and derived ligand models separate from their experimental references.
- Both ligand-bound reference structures replace the catalytic serine with alanine. Their ligand poses inform geometry; WT/PADFL protein preparation uses the 6EQE scaffold candidate.
- QM-start MOL2 files in `ligprep/input/` and files marked `ZERO_PLACEHOLDER` carry zero placeholder charges. The PET3 file marked `GASTEIGER_NOT_RESP` contains Gasteiger charges. None is a final RESP/GAFF topology.
- Experimental ligand poses, isolated charge-optimization geometries, and enzyme-bound pose seeds serve different purposes. Preserve atom identity and document any mapping between them.
- Published author systems require checks of sequence, ligand termini, protonation, reaction state, force field, and software compatibility before reuse. They are not matched project WT/PADFL–PET3 production inputs.
- Complete protein preparation and ligand parameterization, validate matched complexes, then progress through solvation, equilibration, unbiased MD, and a Funnel-MetaD pilot according to CP1–CP7.
- Track small inputs, scripts, decisions, and provenance in Git. Keep large downloads, trajectories, and calculation outputs in project storage under the applicable ignore rules. Before a production run, record the repository commit, software versions, system identity, inputs, checksums, and storage location using the run manifest template.

The project version is stored in [`VERSION`](VERSION). Version tags identify repository snapshots; production readiness is determined separately by the checkpoint evidence.
