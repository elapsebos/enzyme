# 已公开的作者结构与参数

下载日期：2026-11-11。原始下载和派生索引按论文分开保存；没有替换本项目 PET3/PET4、蛋白结构或电荷计算输入。

| 目录 | 电荷/模型 | 实际取得的主要文件 |
|---|---|---|
| jerves_2021_RESP_PET2 | RESP，PET二聚体 | Petasestep1/2.prmtop 与同名 .incpcrd，各2个；作者原坐标扩展名为 .incpcrd，未改名 |
| burgin_2024_CGenFF_PET2 | CGenFF，PET二聚体反应体系 | 两个ZIP：1.acylation、2.deacylation；2个prmtop、2个inpcrd、11个rst7及README |
| berselli_2025_AM1BCC_PET4_PEF4 | AM1-BCC，PET4/PEF4 | PET4和PEF4分别的system_second.prmtop/inpcrd；另有QM相关XYZ，后者不能当作独立完整底物 |
| dipede_2026_RESP_PET4 | RESP，PET4的晶态/非晶态构象研究 | 固定commit的完整GitHub快照和作者ZIP；提取7个PDB、18个GRO、21个TPR及README |

每个来源目录：

- archives/：原始压缩包，保留全部作者内容。
- extracted/：选择性提取结构、拓扑/参数和README，未修改作者文件；不是完整解压。
- archive_inventory.csv：压缩包全部条目的文件名、大小、是否提取和已提取文件SHA256。
- provenance.json：来源、下载地址、压缩包SHA256及仓库校验值或固定commit。
- 仓库原始元数据 JSON：作者、许可/权利描述及原始文件记录，以源仓库为准。

download_summary.json 汇总下载；structure_contents.json 记录已读拓扑/GRO的原子数和残基标签。

核验：Figshare/Zenodo档案与源仓库MD5一致；全部档案记录SHA256。GitHub快照与所记录commit的全部Git blob哈希一致。六组Amber拓扑/初始坐标的原子数匹配。没有运行作者脚本或模拟。

注意：这些是作者计算模型/反应态文件，不是新获得的实验晶体配体。酰化中间体、反应产物、完整底物和QM片段需要进一步区分。GRO/PDB不包含完整的力场或键级定义，TPR版本也需与GROMACS兼容。不能仅按PET2/PET4名称就替换当前配体；当前2026作者GRO中UNK合计90原子，与本项目98原子的工作PET4定义不同，化学身份/端基仍需单独核对。

## 原始来源

- 2021 SI：https://api.figshare.com/v2/articles/16567410 （关联 DOI 10.1021/acscatal.1c03700）
- 2024：https://zenodo.org/records/10854763 （DOI 10.1038/s42004-024-01154-x）
- 2025：https://zenodo.org/records/14697147 （DOI 10.1021/acscatal.5c01263）
- 2026：https://www.plumed-nest.org/eggs/25/029/ 和 https://github.com/fcolizzi/PETase_Cryst-vs-Amor （DOI 10.1021/acs.jpclett.6c00308）

GitHub固定commit：1fa20c6973bca0713c5cd7ad0ded5013c7d4f664。仓库中的小ZIP不含所有GRO/TPR，因此另外保存完整仓库快照。JACS2023的PET3及PADFL2026的独立作者配体包尚未确认，本次不以本项目自建文件冒充作者文件。

重建Figshare/Zenodo下载：python scripts/download_published_structures.py（需要requests）；离线重建全部已有档案的提取和索引：python scripts/index_published_structures.py。GitHub快照可按provenance记录中的codeload固定commit URL重新获取，保留对应commit/tree元数据后再运行离线索引。

大压缩包和解压内容保留本地、不进入Git；来源记录、索引及说明进入Git。原作者内容的使用条件以其仓库记录为准。
