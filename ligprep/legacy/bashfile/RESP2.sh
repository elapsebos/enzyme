#!/bin/bash
#
# Examples:
# RESP2(0.5) for singlet neutral molecule with water solvent: ./RESP2.sh maki.pdb
# RESP2(0.5) for triplet neutral molecule with water solvent: ./RESP2.sh nozomi.xyz 0 3
# RESP2(0.5) for singlet anion with ethanol solvent: ./RESP2.sh nico.mol -1 1 ethanol

# --- 初始化和参数设置 ---
TOTAL_START_TIME=$SECONDS
echo "================================================="
echo "阶段 0: 初始化脚本和参数"
echo "================================================="

delta=0.5
level_opt="B3LYP/def2SVP em=GD3BJ"
level_SP="B3LYP/def2TZVP em=GD3BJ"
Gaussian=g16

export inname=$1
filename=${inname%.*}
suffix=${inname##*.}

if [ -z "$inname" ]; then
    echo "错误: 未提供输入文件！"
    echo "用法: ./RESP2.sh <文件名> [电荷] [自旋多重度] [溶剂]"
    exit 1
fi

if [ $2 ];then
    chg=$2
else
    chg=0
fi

if [ $3 ];then
    multi=$3
else
    multi=1
fi

if [ $4 ];then
    solvent="scrf(solvent="$4")"
else
    solvent="scrf(solvent=water)"
fi

echo "输入文件: $1"
echo "净电荷: $chg"
echo "自旋多重度: $multi"
echo "溶剂模型: $solvent"
echo "RESP2 delta 参数: $delta"
echo "优化计算级别: $level_opt"
echo "单点能计算级别: $level_SP"
echo "初始化完成。总耗时: $(( SECONDS - TOTAL_START_TIME )) 秒。"
echo ""

keyword_opt="# "$level_opt" opt=loose "$solvent" nosymm"
keyword_SP_gas="# "$level_SP" pop=MK IOp(6/33=2,6/42=6) nosymm"
keyword_SP_solv="# "$level_SP" "$solvent" pop=MK IOp(6/33=2,6/42=6) nosymm"

# --- 阶段 1: 坐标格式转换 ---
STAGE_START_TIME=$SECONDS
echo "================================================="
echo "阶段 1: 使用 Multiwfn 进行坐标格式转换"
echo "================================================="
echo "  - 输入: $1"
echo "  - 输出: tmp.xyz"
Multiwfn $1 > /dev/null << EOF
100
2
2
tmp.xyz
0
q
EOF
echo "转换完成。本阶段耗时: $(( SECONDS - STAGE_START_TIME )) 秒。"
echo ""


# --- 阶段 2: 溶剂中几何优化 ---
STAGE_START_TIME=$SECONDS
echo "================================================="
echo "阶段 2: 使用 Gaussian 在溶剂中进行几何优化"
echo "================================================="
echo "  - 输入: tmp.xyz"
echo "  - 输出: gau.gjf, gau.out, gau.chk"
cat << EOF > gau.gjf
%chk=gau.chk
$keyword_opt

Structure Optimization

$chg $multi
EOF
awk '{if (NR>2) print }' tmp.xyz >> gau.gjf
cat << EOF >> gau.gjf


EOF
rm tmp.xyz

echo "开始运行 Gaussian 优化任务..."
$Gaussian < gau.gjf > gau.out
if grep -Fq "Normal termination" gau.out
then
    echo "优化任务成功完成！"
else
    echo "错误: Gaussian 优化任务失败！请检查 gau.out 文件。"
    exit 1
fi
echo "本阶段耗时: $(( SECONDS - STAGE_START_TIME )) 秒。"
echo ""


# --- 阶段 3: 气相单点能和 RESP 电荷计算 ---
STAGE_START_TIME=$SECONDS
echo "================================================="
echo "阶段 3: 气相单点能和 RESP 电荷计算"
echo "================================================="
# 3a: 气相单点能
echo "--- 3a: 运行 Gaussian 进行气相单点能计算 ---"
echo '  - 输入: gau.chk (优化后的几何)' # <-- 已修正
echo "  - 输出: gau.gjf, gau.out"
cat << EOF > gau.gjf
%chk=gau.chk
$keyword_SP_gas geom=allcheck guess=read


EOF
$Gaussian < gau.gjf > gau.out
if grep -Fq "Normal termination" gau.out
then
    echo "气相单点能计算成功完成。"
else
    echo "错误: 气相单点能计算失败！请检查 gau.out 文件。"
    exit 1
fi

# 3b: 生成 fchk 并计算电荷
echo "--- 3b: 运行 formchk 和 Multiwfn 计算气相 RESP 电荷 ---"
echo "  - 输入: gau.chk, gau.out"
echo "  - 输出: gau.fchk, gas.chg"
formchk gau.chk > /dev/null
Multiwfn gau.fchk -ispecial 1 > /dev/null << EOF
7
18
8
1
gau.out
y
0
0
q
EOF
mv gau.chg gas.chg
echo "气相 RESP 电荷已生成到 gas.chg 文件。"
echo "本阶段耗时: $(( SECONDS - STAGE_START_TIME )) 秒。"
echo ""


# --- 阶段 4: 溶剂相单点能和 RESP 电荷计算 ---
STAGE_START_TIME=$SECONDS
echo "================================================="
echo "阶段 4: 溶剂相单点能和 RESP 电荷计算"
echo "================================================="
# 4a: 溶剂相单点能
echo "--- 4a: 运行 Gaussian 进行溶剂相单点能计算 ---"
echo '  - 输入: gau.chk (优化后的几何)' # <-- 已修正
echo "  - 输出: gau.gjf, gau.out"
cat << EOF > gau.gjf
%chk=gau.chk
$keyword_SP_solv geom=allcheck guess=read


EOF
$Gaussian < gau.gjf > gau.out
if grep -Fq "Normal termination" gau.out
then
    echo "溶剂相单点能计算成功完成。"
else
    echo "错误: 溶剂相单点能计算失败！请检查 gau.out 文件。"
    exit 1
fi

# 4b: 生成 fchk 并计算电荷
echo "--- 4b: 运行 formchk 和 Multiwfn 计算溶剂相 RESP 电荷 ---"
echo "  - 输入: gau.chk, gau.out"
echo "  - 输出: gau.fchk, solv.chg"
formchk gau.chk > /dev/null
Multiwfn gau.fchk -ispecial 1 > /dev/null << EOF
7
18
8
1
gau.out
y
0
0
q
EOF
mv gau.chg solv.chg
echo "溶剂相 RESP 电荷已生成到 solv.chg 文件。"
echo "本阶段耗时: $(( SECONDS - STAGE_START_TIME )) 秒。"
echo ""


# --- 阶段 5: 计算 RESP2 电荷并生成最终文件 ---
STAGE_START_TIME=$SECONDS
echo "================================================="
echo "阶段 5: 计算 RESP2 电荷并生成 mol2 文件"
echo "================================================="
chgname=${filename}.chg
# 5a: 计算 RESP2 电荷
echo "--- 5a: 合并气相和溶剂相电荷以计算 RESP2 电荷 ---"
echo "  - 输入: gas.chg, solv.chg"
echo "  - 输出: $chgname"
paste gas.chg solv.chg | awk -v d="$delta" '{printf ("%-3s %12.6f %12.6f %12.6f %15.10f\n",$1,$2,$3,$4,(1-d)*$5+d*$10)}' > $chgname
echo "RESP2 电荷计算完成，结果已保存至 $chgname。"

# 5b: 转换为 PQR 和 MOL2 文件
echo "--- 5b: 使用 Multiwfn 和 OpenBabel 生成最终 mol2 文件 ---"
echo "  - 输入: $chgname"
echo "  - 输出: $filename.pqr, $filename.mol2"
Multiwfn $chgname > /dev/null << EOF
100
2
1
tmp.pqr
0
q
EOF
mv tmp.pqr $filename.pqr
awk 'FNR==NR{if(/^ATOM|^HETATM/)c[++i]=$9;next} {if($0=="@<TRIPOS>ATOM"){a=1;print;next} if($0=="@<TRIPOS>BOND"){a=0} if(a){printf "  %7d %-4s    %10.4f%10.4f%10.4f %-8s%7d %-8s%12.4f\n",$1,$2,$3,$4,$5,$6,$7,$8,c[++j];next}}1' "$filename.pqr" "$filename.mol2" > "$filename.mol2.tmp" && mv "$filename.mol2.tmp" "$filename.mol2"

echo "最终文件 $filename.mol2 已生成。"
echo "本阶段耗时: $(( SECONDS - STAGE_START_TIME )) 秒。"
echo ""


# --- 阶段 6: 清理临时文件 ---
STAGE_START_TIME=$SECONDS
echo "================================================="
echo "阶段 6: 清理临时文件"
echo "================================================="
echo "  - 删除: gau.gjf, gau.fchk, gau.chk, gau.out, gas.chg, solv.chg, ${chgname}"
rm gau.gjf gau.fchk gau.chk gau.out gas.chg solv.chg ${chgname}
echo "清理完成。本阶段耗时: $(( SECONDS - STAGE_START_TIME )) 秒。"
echo ""

# --- 结束 ---
echo "================================================="
echo "脚本执行完毕！"
echo "最终优化的原子坐标和 RESP2 电荷（最后一列）已导出到 $filename.mol2"
echo "脚本总耗时: $(( SECONDS - TOTAL_START_TIME )) 秒。"
echo "================================================="