# fir / Alliance 环境建议查证

查证日期：2026-11-11。Compute Canada 官方技术报告明确表示 actively discourage Anaconda，理由包括其二进制与平台自定义前缀不总兼容，以及可能引入未优化的 OpenMPI/R；平台提供 Python wheels。

原始报告（2022）：https://www.eessi.io/docs/meetings/2022-09-amsterdam/EESSI-community-meeting-2022.09-006-ComputeCanada.pdf

当前 Alliance 的 Anaconda、Python、Fir 文档在本次访问中被反爬机制拒绝，未读取全文。因此不把建议扩大为所有场景的强制禁令，也不猜测 fir 的模块版本。可由用户直接打开：

- https://docs.alliancecan.ca/wiki/Anaconda/en
- https://docs.alliancecan.ca/wiki/Python/en
- https://docs.alliancecan.ca/wiki/Fir/en

本项目采用 modules，必要时使用 module Python 创建的 venv。先前建议在 fir 作业中激活 Conda 不适合此平台，现予纠正。本流程只用标准库，无需安装 Python 依赖。

新增配置：environment.modules、module_init、reject_conda=true。准备/运行阶段拒绝活动 Conda、Conda 管理的 Python/软件路径和相关动态库路径；sbatch 也检查继承的激活状态。未修改用户 .bashrc，不卸载 Conda，不自动清空库路径。作业保存 Python 路径/版本和 LOADEDMODULES。检查覆盖常见环境状态，不保证发现所有污染。

本地模拟测试可明确关闭保护，以便在开发机 Conda Python 下测试；生产配置保持开启。没有在 fir 或真实 QM 软件上执行。
