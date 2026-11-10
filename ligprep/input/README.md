# 待计算配体

HEMT.mol2 与 PET3.mol2 均为显式氢 QM 初始结构，原子部分电荷是零占位，不能当作已完成参数化的配体。

只扫描本目录第一层的 *.mol2。新增 MOL2 后，在 ../config.json 的 ligands 中添加文件名、唯一 id、charge、multiplicity 和 enabled。未知文件会阻止提交，避免猜测电荷态；enabled=false 的配体不提交。

HEMT 与当前中性封端 PET3 为 charge=0、multiplicity=1。MHET 阴离子如需加入，必须显式设置 charge=-1、multiplicity=1。
