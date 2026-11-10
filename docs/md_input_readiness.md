# MD 输入就绪状态

核查日期：2026-11-11。下载/校验成功不等于已批准为本项目生产MD输入。本次只读检查文件与作者说明，没有启动模拟或重新准备蛋白。

## 本项目原有 WT/PADFL

| 文件 | 本次实际检查 | 当前结论 |
|---|---|---|
| structures/prepared/6EQE_WT_chainA_heavy.pdb | 265残基、1952原子、0氢；87Y/121S/186D/233N/246N；催化160S/206D/237H存在 | 蛋白重原子候选；未完成质子化、拓扑、能量优化/溶剂化 |
| structures/prepared/PADFL_from_6EQE_rotamer_preliminary.pdb | 265残基、1949原子、0氢；87F/121P/186A/233L/246D；催化160S/206D/237H存在 | PyMOL侧链rotamer初模；还需局部结构优化和完整准备 |

docs/protonation_table.csv 仍为pending；没有本次新生成的氢或冻结的His互变异构体，也没有收到/发现替代上述初模的Maestro准备结果。PET3仅有初始姿势种子，正式配体RESP/GAFF参数尚未回传；本项目仍没有经验证的WT–PET3/PADFL–PET3生产复合物。

## 下载的作者体系

- Jerves2021：两套Amber拓扑/坐标已有参数和溶剂，原子数分别34821和33876。第二套含SEP修改残基，属于不同反应阶段，不能直接当成普通未反应WT–PET复合物。
- Burgin2024：acylation/README明确说明vmd-md-b.inpcrd是初始反应物坐标，匹配vmd-md-b.prmtop；deacylation/README说明redo-wt2.inpcrd是去酰化前、未最小化的该步骤反应物坐标。其余rst7中包含TS猜测，不应任意挑一个作为结合态MD起点。使用CGenFF/CHARMM体系，不能直接与本项目GAFF/Amber比较视为匹配体系。
- Berselli2025：PET4和PEF4整体系已有prmtop/inpcrd，原子数43168和44671；配体为AM1-BCC/GAFF，不是本项目PET3/RESP。
- DiPede2026：已有GROMACS完整复合物GRO/PDB及TPR，部分为HREX副本、增强采样/拉伸相关输入；需确认副本缩放、偏置、约束与GROMACS/PLUMED版本后才能接续。PDB/GRO自身不含完整拓扑；作者模型UNK合计90原子，与本项目工作PET4的98原子不同。

这些作者体系已具备较多准备结果，可作为文献复现起点，但其构建条件、蛋白序列、质子化、反应状态和力场还需与目标核对。不要从完整复合物删除配体/水后继续使用原拓扑；若改变组成或状态，要重新生成匹配拓扑。

## 建议下一步

本项目WT/PADFL–PET3主线：确定pH、完成两套蛋白一致的准备和记录；完成PET3电荷/力场；生成并检查匹配的两套复合物；再最小化、平衡和短程无偏MD。作者体系另设复现目录，先选论文和反应状态，再沿用对应原始协议做小规模运行检查。
