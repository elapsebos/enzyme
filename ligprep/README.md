# fir 上的配置驱动 RESP2 流程

需要 Python 3.10+、Bash、Slurm，以及 Gaussian+formchk 或 ORCA+orca_2mkl，和 Multiwfn。新流程直接读取显式氢 MOL2，写 XYZ/注入电荷不再依赖 Open Babel 或 PQR。

## 配置和使用

在 fir 上复制 `config.example.json` 为 `config.fir.json`。路径相对于该配置文件所在目录解析；软件名通过计算节点 PATH 查找，或填写绝对路径。配置不是 sbatch 文件，不接受 #SBATCH 语法。

必须填写：`slurm.partition`、`slurm.account`，核对 `time/mem`、可选 `qos/constraint`；设置软件命令和 `environment.setup_shell` 中的 module/source 命令，并记录 `software_versions`。setup_shell 是受信任用户配置的 Bash 命令，不应使用陌生来源内容。

每个 `ligands` 项都必须给出 `id/input/charge/multiplicity`。输入只接受 `.mol2`，包含显式氢、唯一原子名称和完整键连。HEMT/PET3 为 0/1；MHET 阴离子为 -1/1。请先只保留 HEMT 完成真实首测。

```bash
python3 ligprep/resp2_pipeline.py prepare --config ligprep/config.fir.json
# 查看生成的独立工作目录中的 job.sbatch、config.json 和 input.mol2 后提交：
python3 ligprep/resp2_pipeline.py prepare --config ligprep/config.fir.json --submit
```

两次 prepare 会生成两个独立批次；如果已审阅第一批次，要提交该批次可在对应目录执行 `sbatch job.sbatch`，避免重复生成。也可用 `bash ligprep/resp2_orca.sh --config ligprep/config.fir.json [-r]`；Gaussian 使用 `resp2_gaus.sh`。

每个作业自带 runner 副本和配置快照；提交后更新项目脚本不会悄悄改变已排队任务。执行 `run` 的目录如已启动则拒绝重用，失败后用新任务目录重跑以保存证据。

## 两类资源配置

ORCA 示例：`nodes=1, ntasks=16, cpus_per_task=1, omp_threads=1`；`orca_maxcore_mb=1000` 为每进程内存，申请 `mem=32G` 是可调整起点。检查 maxcore×ntasks 不超过申请内存的 75%。ORCA 驱动使用完整路径，由 ORCA 自行启动 MPI；MPI 版本和 fir 启动政策仍需用户核对。

Gaussian：改 `engine` 为 `gaussian`，设 `ntasks=1, cpus_per_task=16, environment.omp_threads=16`；`gaussian_memory=24GB` 必须小于 Slurm `mem=32G`。脚本为各 QM 输入明确写入 `%nprocshared` 和 `%mem`。

`scratch_root=null` 时 Gaussian scratch 位于作业目录；非空时在指定目录创建独立 scratch，路径写入状态记录。ORCA 的临时文件留在各阶段目录，须确保 work_root 文件系统容量/性能合适。脚本不自动删除 scratch/中间记录。

## 科学协议及结果

目前只支持 RESP2：在同一几何上分别计算气相/溶剂电荷，按 delta 混合。不是 HF/6-31G(d) 传统 RESP。JSON 显式保存两引擎各自的方法、溶剂模型和 delta，不能把 ORCA/Gaussian 默认设置当成相同协议。Gaussian 示例显式使用 IEFPCM，对应 legacy 的默认 SCRF 模型；可改为 SMD，但应记录为协议选择。新流程加强 SCF/优化收敛要求，不再沿用 loose 优化。

Multiwfn 的菜单沿用原脚本，完整 stdin/stdout/stderr 保留；需用 fir 安装的 Multiwfn 版本确认拟合选项、限制条件、等价原子处理和菜单含义。自动检查电荷数目、元素顺序、坐标、净电荷和有限值不等于完成 ESP 拟合质量/力场适用性验证。

保留 `opt/`、`gas/`、`solvent/` 的输入、输出、波函数和 `.chg`。`initial.xyz` 是原始坐标；启用优化时另有 `optimized.xyz`。`charges.json` 保存高精度电荷及输入 SHA256/原子映射；`result_RESP2.mol2` 使用原始输入坐标、完整键连和原子名，写十位小数，标签为 USER_CHARGES。`run_status.json` 记录状态、程序路径、资源及版本声明。最终 MOL2 是电荷文件，尚需 GAFF/GAFF2 类型与拓扑准备。

安全重写电荷只能使用本流程生成的 charges.json：

```bash
bash ligprep/fix.sh --mol2 INPUT.mol2 --charge-record charges.json --output NEW.mol2
```

会检查输入哈希、原子身份与净电荷，拒绝覆盖输入或已有输出。旧的按 PQR 第九列和行序批量覆盖方式已退役。

## 迁移与验证边界

原始脚本完整保留在 `legacy/`，仅供追溯。活动入口改为配置驱动，不再接受旧 `-i` 选项；`bashfile/*noopt.sh` 通过 `--no-optimize` 生成任务；旧 calcRESP 独立拟合入口停止使用，以免绕过检查。旧 YAML 表位于 legacy，实际配置只使用 JSON。

本地测试使用模拟 QM/Multiwfn 输出验证配置、原子映射、失败处理和两条编排路线；没有在 fir 或真实 QM 程序上执行。首个 HEMT 作业仍需检查优化收敛、软件兼容性、拟合日志、ESP质量和实际资源用量，再扩展到 PET3。
