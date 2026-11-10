# 配体电荷批量计算

目录：input/ 放待算 MOL2；scripts/ 放运行程序与测试；output/ 放结果；config.json 是实际配置；run.sh 为统一入口。config.example.json 是传统 RESP 示例；config.resp2.example.json 是 RESP2 示例。legacy/ 仅供追溯。

需要 Python 3.10+、Bash、Slurm，以及所选 QM/拟合程序。Python 无额外依赖。新流程不使用 Open Babel 或 PQR。

## 运行

1. 将待算显式氢 MOL2 放入 input/。已放入 HEMT.mol2、PET3.mol2，原子电荷都是零占位。
2. 编辑 config.json，填写 fir 账户、分区、软件环境和资源，并检查 ligands 中各文件的 charge、multiplicity、enabled。
3. 从 enzyme 目录执行 bash ligprep/run.sh；从 ligprep 目录执行 bash run.sh。

execution.submit=false 时只在 output/ 下生成独立任务。检查 job.sbatch 后进入任务目录执行 sbatch job.sbatch。若设为 true，run.sh 会自动生成并提交；也可临时使用 bash ligprep/run.sh --submit。登录节点只负责准备与提交，计算在 Slurm 分配的节点上执行。

每次运行创建一个新批次，再次运行可能重复提交。若已审阅生成的任务，直接在其目录 sbatch job.sbatch，避免再次生成。每个任务都复制输入、配置和 runner，后续项目变更不影响已排队任务。

也可以执行 python3 ligprep/scripts/ligprep.py prepare --config ligprep/config.json [--submit]。

只扫描 input/ 第一层 *.mol2。新增文件必须在 ligands 中配置文件名、唯一id、电荷和多重度，否则拒绝提交；enabled=false 跳过。文件缺失、原子名重复、原子数/键连错误、电荷自旋不匹配也会失败。不要自动猜测中性态。

## 科学协议

默认传统 RESP：Gaussian 气相 HF/6-31G(d) 优化和 ESP 单点，经 AmberTools espgen、antechamber、respgen 和两阶段 resp 拟合。需要 g16、formchk、antechamber、espgen、respgen、resp，不需要 Multiwfn。不计算溶剂单点，不进行 delta 混合。

这与当前 PET3 文献所述 HF/6-31G(d)/RESP 方法对齐，但并不证明完全复现所有细节。ESP 网格、等价原子约束、构象数和优化约定仍需对照论文SI；拟合输入结果全部保留。respgen 的控制参数在 resp1.in/resp2.in 中；resp2.in 表示第二阶段拟合输入，不是 RESP2 电荷协议。

可选 RESP2：将 config.resp2.example.json 复制为 config.json 后填写 fir 设置。示例为 ORCA+Multiwfn，在同一溶剂优化几何上计算气相/溶剂电荷并按 delta 混合。Gaussian 也支持 RESP2，但须设置正确的共享内存布局与方法/溶剂模型。

支持：RESP = Gaussian+AmberTools；RESP2 = Gaussian或ORCA+Multiwfn。不支持的组合在准备阶段报错。只改 protocol 字符串不等于切换完整协议。同一 WT/PADFL 对照中，同一配体应采用同一电荷协议。Multiwfn菜单需与 fir 安装版本核对。

## 配置

- slurm：partition、account 必填；time/mem、qos/constraint/licenses 按 fir 规范填写。
- environment.setup_shell：受信任的 module/source/export 命令，在计算节点执行。python 是节点可用的 Python 命令。
- programs：软件名通过计算节点 PATH 查找，或填写绝对路径。software_versions 记录版本。
- chemistry：协议、fit_backend、优化/单点方法、溶剂模型、delta和检查容差；传统 RESP 不使用溶剂与delta，delta为null。
- input_directory 默认 input，work_root 默认 output；相对路径均以配置文件所在目录为基准。
- scratch_root=null 时 Gaussian scratch 位于任务目录；非空时使用指定位置的独立目录。ORCA 临时文件在各计算阶段目录，work_root 需要容量与性能合适。

Gaussian 示例：1节点、ntasks=1、cpus_per_task=16、omp_threads=16，申请32G，程序设置24GB。ORCA 示例：1节点、ntasks=16、cpus_per_task=1、omp_threads=1，每进程maxcore=1000MB、申请32G。这些是待 fir 政策与首次实测确认的起点，不是资源或用时保证。

## 结果与验证

每个 output/任务目录保留 input.mol2、config.json、job.sbatch、runner、initial.xyz、可选optimized.xyz、各阶段输入/输出/波函数/拟合数据、charges.json、run_status.json。不会自动清理计算证据。

result_RESP.mol2 或 result_RESP2.mol2 保留原始输入几何、键连和原子名，注入高精度电荷；优化后的孤立分子几何另存。最终MOL2不是完整GAFF/GAFF2拓扑，仍需类型与参数准备。原子数/顺序/坐标、净电荷、程序退出状态和优化收敛均受检查，但这些检查不能替代 ESP 拟合质量与力场适用性评估。

重新注入同一电荷记录：python3 ligprep/scripts/ligprep.py inject-charges --mol2 INPUT.mol2 --charge-record charges.json --output NEW.mol2。检查输入SHA256和原子身份，拒绝覆盖。已有状态文件的任务目录拒绝直接重复运行，失败后请新建批次。

本地测试使用模拟 QM/拟合输出；尚未在 fir 实测。建议先将PET3的enabled设为false，只启用HEMT确认环境、日志、拟合约束与资源用量，再启用PET3。

AmberTools 两阶段流程参考：https://dev-archive.ambermd.org/200603/att-0122/amber9.pdf 。接口以 fir 安装版本手册为准。
