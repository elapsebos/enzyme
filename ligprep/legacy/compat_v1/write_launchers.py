"""Regenerate thin Bash launchers; original scripts are in legacy/."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
for name, engine in [('resp2_orca.sh', 'orca'), ('resp2_gaus.sh', 'gaussian')]:
    text = '''#!/bin/bash
set -euo pipefail
script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
config=""
submit=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    -c|--config) config="${2:?Configuration path required}"; shift 2 ;;
    -r|--run) submit=(--submit); shift ;;
    -h|--help) echo "Usage: bash $0 --config config.json [-r]"; exit 0 ;;
    *) echo "Unknown option: $1. Use --config; ligand paths/charges are configured there." >&2; exit 2 ;;
  esac
done
[[ -n "$config" ]] || { echo "--config is required" >&2; exit 2; }
exec "${PYTHON_BIN:-python3}" "$script_dir/resp2_pipeline.py" prepare --engine ENGINE --config "$config" "${submit[@]}"
'''.replace('ENGINE', engine)
    (ROOT / name).write_text(text, encoding='utf-8', newline='\n')

(ROOT / 'fix.sh').write_text('''#!/bin/bash
set -euo pipefail
script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
exec "${PYTHON_BIN:-python3}" "$script_dir/resp2_pipeline.py" inject-charges "$@"
''', encoding='utf-8', newline='\n')

for name, engine, noopt in [('RESP2_ORCA.sh', 'orca', False), ('RESP2_ORCA_noopt.sh', 'orca', True),
                             ('RESP2.sh', 'gaussian', False), ('RESP2_noopt.sh', 'gaussian', True)]:
    text = '''#!/bin/bash
set -euo pipefail
script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
# Migration: --config is required; this creates jobs, it does not run QM on a login node.
exec "${PYTHON_BIN:-python3}" "$script_dir/resp2_pipeline.py" prepare --engine ENGINE NOOPT "$@"
'''.replace('ENGINE', engine).replace('NOOPT', '--no-optimize' if noopt else '')
    (ROOT / 'bashfile' / name).write_text(text, encoding='utf-8', newline='\n')
(ROOT / 'bashfile' / 'calcRESP.sh').write_text('''#!/bin/bash
echo "Legacy fitting entry point retired. Use resp2_pipeline.py prepare --config CONFIG.json. Original helper: legacy/bashfile/calcRESP.sh" >&2
exit 2
''', encoding='utf-8', newline='\n')
