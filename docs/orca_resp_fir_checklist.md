# ORCA 气相 RESP：fir 配置待办

用户说明 Gaussian 需要额外申请授权，当前默认改用 ORCA，不因此改成 RESP2。

已更新：engine=orca，protocol=RESP，fit_backend=multiwfn；ORCA 优化 HF 6-31G* Opt TightSCF，单点 HF 6-31G* TightSCF；不加溶剂、不混合电荷；单节点16进程、1CPU/进程、OMP=1，MaxCore=1000MB/进程，总内存32G。资源是待首测确认的起点。

候选模块 python/3.11.5、orca/6.1.1、multiwfn/3.8 已列为可查询版本，但依赖组合尚未验证。当前不加载 Gaussian、Amber、GROMACS或PLUMED；没有沿用 Amber 的 OpenMPI 配置以免误配 ORCA。

## 必须在 fir 确认/填写

1. module spider orca/6.1.1、multiwfn/3.8、python/3.11.5 的完整依赖行。据此在 environment.modules 中补齐兼容的 StdEnv/编译器/MPI；不要猜测 ORCA 的 MPI 版本。
2. slurm.partition 和 account 目前仍为 null；按实际授权填写。time=24h、mem=32G、16进程也需符合分区限制。
3. 加载后 command -v orca orca_2mkl Multiwfn python3 均能解析。工具不在 PATH 时修改 programs 中的绝对路径，尤其确认 orca 与 orca_2mkl 来自同一安装。
4. 确认 Multiwfn module 是否设置 Multiwfnpath，以及 settings.ini 的来源、nthreads和拟合配置。不能假定 OMP_NUM_THREADS 一定覆盖 Multiwfn 自身线程设置；首测可使用 nthreads=1。
5. 若 batch 中 module 未初始化，填写 environment.module_init 为 fir 实际初始化文件。记录软件真实版本，不能把候选模块名当作计算成功证明。
6. work_root=output 为项目共享目录；确认可计算且有足够容量。ORCA 临时文件位于各阶段目录。scratch_root 当前只控制 Gaussian scratch，不要误认为设置它就会迁移 ORCA 工作文件。
7. 当前 HEMT enabled=true、PET3=false。首测后核对 Multiwfn菜单、拟合网格/约束、原子顺序、净电荷及资源用量，再启用PET3。execution.submit仍为false，先生成检查后提交。

## 方法边界

HF 6-31G* 与 HF/6-31G(d) 是常见的基组命名对应，但不同程序的球谐/笛卡尔约定可能不同。Multiwfn拟合与Gaussian MK ESP/AmberTools两阶段拟合也不能默认等价。若必须逐项复现目标论文，应核对原文/SI的网格、基函数约定和约束，而不只比较方法名称。

ORCA原生!RESP以其CHELPG网格加约束实现，并不是这里自动使用的后端：
https://www.faccts.de/docs/orca/6.1/manual/contents/spectroscopyproperties/population.html

这次仅本地模拟流程验证，未登录 fir 或执行真实 QM。
