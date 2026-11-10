#!/bin/bash
set -euo pipefail
ligprep_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
exec "${PYTHON_BIN:-python3}" "$ligprep_dir/scripts/ligprep.py" prepare --config "$ligprep_dir/config.json" "$@"
