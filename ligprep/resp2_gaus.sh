#!/bin/bash
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
exec "${PYTHON_BIN:-python3}" "$script_dir/resp2_pipeline.py" prepare --engine gaussian --config "$config" "${submit[@]}"
