#!/bin/bash

# Exit on any error
set -e

# --- Script Usage ---
if [ $# -lt 1 ]; then
    echo "Usage: $0 <dir1> [dir2 dir3 ...]"
    echo "       Example: $0 ./dir1 ./dir2"
    echo "       Or:      $0 ./ligands/*"
    exit 1
fi

# This function unconditionally replaces charges in a MOL2 file
# with charges from a corresponding PQR file.
update_mol2_charges() {
    local pqr_file="$1"
    local mol2_file="$2"
    local tmp_mol2_file="${mol2_file}.tmp"

    echo "🔄 [UPDATING] Applying charges from $pqr_file -> $mol2_file"

    # Awk command to replace the charge column ($9) in the MOL2 file
    # while preserving the original formatting.
    if awk '
        FNR==NR {if (/^ATOM|^HETATM/) c[++i]=$9; next}
        {
            if ($0 == "@<TRIPOS>ATOM") { a=1; print; next }
            if ($0 == "@<TRIPOS>BOND") { a=0 }
            if (a) {
                printf "  %7d %-4s    %10.4f%10.4f%10.4f %-8s%7d %-8s%12.4f\n", \
                       $1, $2, $3, $4, $5, $6, $7, $8, c[++j]
                next
            }
        }
        1' "$pqr_file" "$mol2_file" > "$tmp_mol2_file"; then
        
        # If awk command was successful, replace the original file
        mv "$tmp_mol2_file" "$mol2_file"
        echo "✅ [DONE] Successfully updated $mol2_file"
    else
        # If awk failed, print an error and remove the temp file
        echo "❌ [ERROR] Failed to update $mol2_file. Rolling back."
        rm -f "$tmp_mol2_file"
        return 1
    fi
}

# Export the function so it's available in the subshell created by the pipeline
export -f update_mol2_charges

# --- Main Execution Loop ---
# Loop over all directories provided as arguments
for input_path in "$@"; do
    # Find all .pqr files and process them
    find "$input_path" -type f -name "*.pqr" | while read -r pqr; do
        # Define the corresponding .mol2 file path
        mol2="${pqr%.pqr}.mol2"
        
        # If the .mol2 file exists, perform the update
        if [ -f "$mol2" ]; then
            update_mol2_charges "$pqr" "$mol2"
        fi
    done
done
