#!/bin/bash
#
# Examples:
# RESP2(0.5) for singlet neutral molecule with water solvent: ./RESP2_ORCA.sh maki.pdb
# RESP2(0.5) for triplet neutral molecule with water solvent: ./RESP2_ORCA.sh nozomi.xyz 0 3
# RESP2(0.5) for singlet anion with ethanol solvent: ./RESP2_ORCA.sh nico.mol -1 1 ethanol

# --- 阶段 0: 初始化与参数设置 ---
TOTAL_START_TIME=$SECONDS

# 设置 ORCA 和 orca_2mkl 的路径
ORCA="/home/zhutao/scratch/orca610/bin/orca"
orca_2mkl="/home/zhutao/scratch/orca610/bin/orca_2mkl"

# 检查必要程序
for cmd in "$ORCA" "$orca_2mkl" Multiwfn obabel; do
    if ! command -v $cmd &> /dev/null; then
        echo "错误: 找不到命令 '$cmd'。"
        exit 1
    fi
done

nprocs=16
maxcore=1000
delta=0.5
keyword_opt="! B97-3c opt"
keyword_SP="! B3LYP/G D3 def2-TZVP def2/J RIJCOSX"

export inname=$1
filename=${inname%.*}

if [ -z "$inname" ]; then
    echo "错误: 未提供输入文件！"
    exit 1
fi

### 解析参数
if [ "$2" ];then chg=$2; else chg=0; fi
if [ "$3" ];then multi=$3; else multi=1; fi
if [ "$4" ];then solvent=$4; else solvent="Water"; fi

echo "Processing $inname | Charge: $chg | Multi: $multi | Solvent: $solvent"

# --- 阶段 1: 坐标转换 ---
Multiwfn "$1" > /dev/null << EOF
100
2
2
tmp.xyz
0
q
EOF

# --- 阶段 2: 几何优化 ---
cat << EOF > opt.inp
$keyword_opt
%maxcore $maxcore
%pal nprocs $nprocs end
%geom Convergence loose end
%cpcm
smd true
SMDsolvent "$solvent"
end
EOF
echo "* xyz $chg $multi" >> opt.inp
awk '{if (NR>2) print }' tmp.xyz >> opt.inp
echo "*" >> opt.inp

echo "Running ORCA Optimization..."
$ORCA opt.inp > opt.out

if grep -Fq "ORCA TERMINATED NORMALLY" opt.out
then
    mv opt.xyz tmp.xyz
    # 清理优化中间文件
    rm opt.inp opt.out opt.trj opt.gbw opt.prop opt_property.txt opt.hess 2>/dev/null
else
    echo "Error: Optimization failed!"
    exit 1
fi

# --- 阶段 3: 气相单点能 ---
cat << EOF > SP.inp
$keyword_SP
%maxcore $maxcore
%pal nprocs $nprocs end
EOF
echo "* xyz $chg $multi" >> SP.inp
awk '{if (NR>2) print }' tmp.xyz >> SP.inp
echo "*" >> SP.inp

echo "Running ORCA Gas SP..."
$ORCA SP.inp > SP.out
if ! grep -Fq "ORCA TERMINATED NORMALLY" SP.out; then echo "Error: Gas SP failed"; exit 1; fi

$orca_2mkl SP -molden > /dev/null
mv SP.molden.input SP.molden

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

# --- 阶段 4: 溶剂相单点能 ---
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

echo "Running ORCA Solvent SP..."
$ORCA SP.inp > SP.out
if ! grep -Fq "ORCA TERMINATED NORMALLY" SP.out; then echo "Error: Solvent SP failed"; exit 1; fi

$orca_2mkl SP -molden > /dev/null
mv SP.molden.input SP.molden

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

# --- 阶段 5: 生成最终文件 ---
chgname=${filename}.chg
paste gas.chg solv.chg | awk -v d="$delta" '{printf ("%-3s %12.6f %12.6f %12.6f %15.10f\n",$1,$2,$3,$4,(1-d)*$5+d*$10)}' > $chgname

# 生成 Mol2 (保留 Docking Pose)
if command -v obabel &> /dev/null; then
    obabel "$inname" -o mol2 -O "$filename.mol2"
else
    echo "Error: obabel missing."
    exit 1
fi

Multiwfn "$chgname" > /dev/null << EOF
100
2
1
tmp.pqr
0
q
EOF
mv tmp.pqr "$filename.pqr"

awk 'FNR==NR{if(/^ATOM|^HETATM/)c[++i]=$9;next} {if($0=="@<TRIPOS>ATOM"){a=1;print;next} if($0=="@<TRIPOS>BOND"){a=0} if(a){printf "  %7d %-4s    %10.4f%10.4f%10.4f %-8s%7d %-8s%12.4f\n",$1,$2,$3,$4,$5,$6,$7,$8,c[++j];next}}1' "$filename.pqr" "$filename.mol2" > "$filename.mol2.tmp" && mv "$filename.mol2.tmp" "$filename.mol2"

# --- 阶段 6: 清理 ---
rm SP.* gas.chg solv.chg tmp.xyz "$filename.pqr" "$chgname" 2>/dev/null

echo "================================================="
echo "Done! Result: $filename.mol2"
echo "Total Time: $(( SECONDS - TOTAL_START_TIME ))s"
echo "================================================="