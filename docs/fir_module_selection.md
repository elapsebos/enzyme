# fir 模块选择记录

依据：用户提供的 fir `module spider` 输出（2026-11-11）。只证明软件在模块树中可查询，不证明账户授权、模块组合已成功加载或所需可执行程序已运行。

以下为先前 Gaussian/AmberTools 的历史候选链，现保存在 config.gaussian-resp.example.json。用户因 Gaussian 授权要求选择 ORCA；当前实际配置以 docs/orca_resp_fir_checklist.md 为准：

```text
StdEnv/2023
gcc/12.3
openmpi/4.1.5
python/3.11.5
gaussian/g16.c01
amber/22.5-23.5
```

其中 amber 的 StdEnv/gcc/openmpi 依赖来自用户提供的完整 spider 输出；Python 3.11.5 和 Gaussian C.01 已列为可用版本，但其依赖尚未提供，因此整个组合仍是待 fir 实测的候选，不能称已验证环境。

在 fir 继续查询：

```bash
module spider python/3.11.5
module spider gaussian/g16.c01
module spider ambertools
```

若输出要求不同 StdEnv/编译器，应选择与 AmberTools 一致的依赖链，而不是忽略 module load 的错误或自动切换。Amber-PMEMD 模块说明明确不包含 AmberTools，不能替代 antechamber/espgen/respgen/resp。单独 ambertools 模块如提供这些工具，可在确认依赖后替代完整 amber 模块。

依赖一致后，按配置顺序加载并检查：

```bash
module load StdEnv/2023 gcc/12.3 openmpi/4.1.5
module load python/3.11.5 gaussian/g16.c01 amber/22.5-23.5
module list
python3 --version
for tool in python3 g16 formchk antechamber espgen respgen resp; do
    command -v "$tool" || echo "MISSING: $tool"
done
```

登录时若自动激活 Conda，先正常退出其全部激活层级，然后加载 modules；不要仅 unset Conda 变量。以上检查还须在首次 Slurm 任务中验证，登录节点可用不等于计算节点可用。

ORCA 可查询 6.1.1、Multiwfn 可查询 3.8，但 ORCA 的 MPI 和其他前置依赖尚未给出；因此没有把未经确认的 ORCA/MPI 组合填进 RESP2 示例。当前传统 RESP 路线无需 ORCA/Multiwfn/GROMACS/PLUMED。后续 MD 阶段再独立检查 gromacs-plumed 和其集成 PLUMED 的版本，避免与 QM 环境混装。
