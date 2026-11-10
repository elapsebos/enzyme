#!/bin/bash
#
# Examples:
# RESP2(0.5) for singlet neutral molecule with water solvent: ./RESP2_ORCA_noopt.sh maki.pdb
# RESP2(0.5) for triplet neutral molecule with water solvent: ./RESP2_ORCA_noopt.sh nozomi.xyz 0 3
# RESP2(0.5) for singlet anion with ethanol solvent: ./RESP2_ORCA_noopt.sh nico.mol -1 1 ethanol

#Set actual paths of ORCA and orca_2mkl utility here
ORCA="/home/zhutao/scratch/orca610/bin/orca"
orca_2mkl="/home/zhutao/scratch/orca610/bin/orca_2mkl"

#Set number of CPU cores used in calculation here
nprocs=16
maxcore=1000

delta=0.5
keyword_SP="! B3LYP/G D3 def2-TZVP def2/J RIJCOSX"

export inname=$1
filename=${inname%.*}
suffix=${inname##*.}

# Check input
if [ -z "$inname" ]; then
    echo "Error: No input file provided."
    exit 1
fi

### Parse arguments
if [ "$2" ];then chg=$2; else chg=0; fi
if [ "$3" ];then multi=$3; else multi=1; fi
if [ "$4" ];then solvent=$4; else solvent="Water"; fi

echo "Input: $inname"
echo "Charge: $chg, Multiplicity: $multi"
echo "Solvent: $solvent"
echo "Delta: $delta"

### Convert current file to tmp.xyz
Multiwfn "$1" > /dev/null << EOF
100
2
2
tmp.xyz
0
q
EOF

# --- Phase 1: Gas Phase Single Point ---
echo
echo "Running single point task in gas via ORCA..."
cat << EOF > SP.inp
$keyword_SP
%maxcore $maxcore
%pal nprocs $nprocs end
EOF
echo "* xyz $chg $multi" >> SP.inp
awk '{if (NR>2) print }' tmp.xyz >> SP.inp
echo "*" >> SP.inp

$ORCA SP.inp > SP.out

if grep -Fq "ORCA TERMINATED NORMALLY" SP.out
then
    echo "Gas phase calculation Done!"
else
    echo "Error: Gas phase calculation failed. Check SP.out."
    exit 1
fi

# Convert to .molden file (No Nval)
echo "Running orca_2mkl..."
$orca_2mkl SP -molden > /dev/null
mv SP.molden.input SP.molden

# Calculate RESP charges in gas
echo "Running Multiwfn (Gas RESP)..."
Multiwfn SP.molden -ispecial 1 > /dev/null << EOF
7
18
1
y
0
0
q
EOF
mv SP.chg gas.chg
echo "Gas phase charges generated."

# --- Phase 2: Solvent Phase Single Point ---
echo
echo "Running single point task in solvent via ORCA..."
cat << EOF > SP.inp
$keyword_SP
%maxcore $maxcore
%pal nprocs $nprocs end
%cpcm
smd true
SMDsolvent "$solvent"
end
EOF
echo "* xyz $chg $multi" >> SP.inp
awk '{if (NR>2) print }' tmp.xyz >> SP.inp
echo "*" >> SP.inp
# rm tmp.xyz # Keep tmp.xyz for safety until end

$ORCA SP.inp > SP.out

if grep -Fq "ORCA TERMINATED NORMALLY" SP.out
then
    echo "Solvent phase calculation Done!"
else
    echo "Error: Solvent phase calculation failed. Check SP.out."
    exit 1
fi

# Convert to .molden file (No Nval)
echo "Running orca_2mkl..."
$orca_2mkl SP -molden > /dev/null
mv SP.molden.input SP.molden

# Calculate RESP charge in solvent
echo "Running Multiwfn (Solvent RESP)..."
Multiwfn SP.molden -ispecial 1 > /dev/null << EOF
7
18
1
y
0
0
q
EOF
mv SP.chg solv.chg
echo "Solvent phase charges generated."

# Clean up intermediate files
rm SP.* SP_* tmp.xyz

### Calculate RESP2 charges
chgname=${filename}.chg
paste gas.chg solv.chg | awk -v d="$delta" '{printf ("%-3s %12.6f %12.6f %12.6f %15.10f\n",$1,$2,$3,$4,(1-d)*$5+d*$10)}' > $chgname

echo
echo "RESP2 charges calculated."

### Generate Final Mol2 (Preserving Docking Pose)
echo "Generating final mol2 file..."

# 1. Use obabel to create template from ORIGINAL input file
if command -v obabel &> /dev/null; then
    obabel "$inname" -o mol2 -O "$filename.mol2"
else
    echo "Error: obabel not found."
    exit 1
fi

# 2. Extract charge column using PQR format
Multiwfn "$chgname" > /dev/null << EOF
100
2
1
tmp.pqr
0
q
EOF
mv tmp.pqr "$filename.pqr"

# 3. Inject RESP2 charges into the template
awk 'FNR==NR{if(/^ATOM|^HETATM/)c[++i]=$9;next} {if($0=="@<TRIPOS>ATOM"){a=1;print;next} if($0=="@<TRIPOS>BOND"){a=0} if(a){printf "  %7d %-4s    %10.4f%10.4f%10.4f %-8s%7d %-8s%12.4f\n",$1,$2,$3,$4,$5,$6,$7,$8,c[++j];next}}1' "$filename.pqr" "$filename.mol2" > "$filename.mol2.tmp" && mv "$filename.mol2.tmp" "$filename.mol2"

# Final Cleanup
rm "$filename.pqr" "$chgname" gas.chg solv.chg

echo "Finished! Result saved to $filename.mol2"