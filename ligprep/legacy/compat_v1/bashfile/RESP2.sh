#!/bin/bash
set -euo pipefail
script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
# Migration: --config is required; this creates jobs, it does not run QM on a login node.
exec "${PYTHON_BIN:-python3}" "$script_dir/resp2_pipeline.py" prepare --engine gaussian  "$@"
