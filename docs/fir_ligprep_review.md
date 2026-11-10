# ligprep 脚本解析与 fir 集群配置清单

检查日期：2026-11-11。下述问题针对最初复制来的脚本。当前已采用 input/、scripts/、output/、config.json 和 run.sh 布局；默认传统 RESP，RESP2 为可选协议。原脚本位于 legacy/；当前说明见 ligprep/README.md。尚未在 fir 或真实 QM 软件上执行。

## 实际计算流程

这套脚本计算 RESP2(0.5)，不是此前讨论的 HF/6-31G(d) 气相 RESP。气相与溶剂相分别拟合电荷，再按 q = 0.5 q_gas + 0.5 q_solvent 混合。最终结果还需另行分配 GAFF/GAFF2 类型、补参数和生成模拟拓扑。

| 文件 | 作用 |
|---|---|
| ligprep/resp2_orca.sh | 为输入文件建立独立目录并生成 sbatch；带 -r 时提交 |
| ligprep/resp2_gaus.sh | Gaussian 版本的提交脚本 |
| ligprep/bashfile/RESP2_ORCA.sh | B97-3c 溶剂优化；B3LYP/G D3 def2-TZVP/def2-J RIJCOSX 气相和 SMD 溶剂单点；Multiwfn 拟合与混合 |
| ligprep/bashfile/RESP2.sh | B3LYP/def2SVP + GD3BJ 溶剂优化；B3LYP/def2TZVP + GD3BJ 气相和 SCRF 溶剂单点；Multiwfn 拟合与混合 |
| 两个 *_noopt.sh | 跳过几何优化，直接在输入坐标做单点与电荷计算；Gaussian noopt 的方法设置也与优化版不同 |
| calcRESP.sh | 从一个或两个波函数文件调用 Multiwfn 拟合；两个文件时混合为 RESP2 |
| fix.sh | 按原子行序，把 PQR 的第九列写入 MOL2 部分电荷列 |

Gaussian/ORCA 分支的优化方法、色散和溶剂处理并不完全一致；不得仅因都称 RESP2 就视为同一协议。Multiwfn 菜单调用和拟合默认选项也须与 fir 安装版本核对。

## 运行前需修正的问题

1. 提交器硬编码 /home/zhutao 路径、xh321 分区、weiwang 账户和 source 环境文件。均未证明适用于 fir。
2. 提交器用 sh 调用含 Bash 特性的 worker；应显式使用 bash。
3. 两个提交器仅传文件名，未传总电荷、多重度和溶剂；因此当前默认把所有配体按中性单重态处理，不能直接提交 MHET 阴离子。
4. ORCA worker 使用 obabel "$inname" -O "$filename.mol2"。当输入本身为 MOL2 时，读写同一路径有覆盖/截断风险；应先生成不同名称的模板，最终结果也用独立文件名。
5. Gaussian worker 注入电荷前未生成 MOL2 模板，依赖同名 MOL2 已存在；输入其他格式时可能失败。输入为 MOL2 时也会覆盖原输入。
6. ORCA 固定 nprocs=16、maxcore=1000 MB/进程；Gaussian 输入没有显式 %nprocshared/%mem，是否由集群环境补充未知。仅申请 Slurm 核数不能保证 Gaussian 使用对应资源。
7. opt/SP 的输入输出被覆盖或删除，gas.chg/solv.chg 和混合电荷也被删掉。应分别保留优化、气相、溶剂日志、输入、波函数/ESP 或拟合证据、原始电荷和最终结果。
8. Multiwfn/Open Babel 的每步退出码、拟合是否完成、原子数/顺序、净电荷尚未充分检查；只看 QM 正常终止字样不等于几何优化已收敛。
9. PQR 第九列是否为电荷取决于具体格式，尤其是否含 chain 字段；需与本机 Multiwfn 输出核对。按行直接注入电荷还需显式原子映射和数目检查。
10. 最终 MOL2 电荷保留四位小数且未记录可靠的电荷方法标签；需要保留高精度电荷和检查净电荷，不能依赖输出文件名证明计算正确。
11. 目录/通配符输入会遍历所有普通文件，未按结构格式筛选。Slurm 输出路径为相对路径，shell 中后续 cd 不会改变 Slurm 预先打开日志的位置。
12. 使用单个输入构象计算电荷；PET3 等柔性配体是否采用多构象拟合仍需单独决定。

## 请提供的 fir 配置

| 信息 | 需要的具体内容 |
|---|---|
| 集群身份/参考 | fir 所属机构或官方计算说明；最好提供一份本人已成功运行的 sbatch |
| 调度 | partition、account、可选 qos/constraint、允许的最长时间、是否有 license 请求要求 |
| 资源 | 节点 CPU 数与内存、建议任务布局、可申请内存、walltime；是否限制并发任务 |
| QM 软件 | 选 Gaussian 或 ORCA；版本、module load/source 指令、可执行文件路径；ORCA 对应 MPI 环境 |
| 辅助程序 | Multiwfn 版本与可执行命令；Open Babel 版本与命令；Gaussian 的 formchk 或 ORCA 的 orca_2mkl 路径 |
| 文件系统 | enzyme/ligprep 在 fir 的绝对路径、输入目录、结果目录、scratch 路径/配额、作业结束后的保留与清理政策 |
| 科学设置 | 传统 RESP 或此脚本的 RESP2(0.5)、优化/单点方法、溶剂；各配体净电荷和自旋多重度 |

不需要提供密码、私钥或 token。已运行成功的脚本中的账户名、分区、module 指令和目录足够用于适配。

## 可讨论的资源起点（非 fir 已确认配置）

- ORCA：单节点、16 MPI 进程、每进程 1 CPU；worker 的 nprocs 同样设置 16。若保持 maxcore=1000 MB/进程，可先申请 32G 总内存，给程序其他分配留余量。并非所有体系都会在此设置下完成。
- Gaussian：单节点、1 task、16 CPUs/task；输入中显式设置 %nprocshared=16，并使 %mem 小于 Slurm 总内存，例如申请 32G 时设置 24GB。需核对 fir 的 Gaussian 启动规范。
- walltime、scratch 容量和最终核数以 fir 政策及 HEMT 首次任务实测为依据；没有基准前不承诺 PET3 用时。
- 每个配体/电荷态使用独立工作目录。HEMT 和当前 PET3 为 0/1；MHET 阴离子为 -1/1，需显式传参。

ORCA 官方建议 maxcore × nprocs 不超过可用内存约 75%，并使用完整可执行路径启动其驱动程序，不能仅靠 Slurm 核数自动开启并行。

## 官方参考

- Slurm sbatch：https://slurm.schedmd.com/sbatch.html
- ORCA 并行：https://orca-manual.mpi-muelheim.mpg.de/contents/essentialelements/parallel.html
- ORCA 内存：https://orca-manual.mpi-muelheim.mpg.de/contents/quickstartguide/troubleshooting.html
