# PETase 文献：电荷方法与配体文件披露核对

核对日期：2026-11-11。区分方法名称、已公开文件清单、实际下载检查三种证据。本次未下载大型作者数据包，也未用作者拓扑替换本项目输入。

| 文献 | 电荷/配体模型 | 文件披露证据 |
|---|---|---|
| Jerves et al., ACS Catal. 2021, DOI 10.1021/acscatal.1c03700 | PET二聚体，HF/6-31G(d) RESP；GAFF2。已核对本地原文 | 正文及出版社SI清单明确列出 Topology and coordinate files (ZIP)。确认有机器可读数据包，尚未检查包内文件名 |
| García-Meseguer et al., JACS 2023, DOI 10.1021/jacs.3c04427 | PET3，Gaussian09 HF/6-31G(d) RESP + GAFF。已核对正文 | 出版社及正文仅明确列出PDF补充材料；本次未确认独立MOL2、拓扑或坐标数据包。不能将“未找到”写成“确定未公开” |
| Zhang et al., PADFL, Bioresour. Technol. 2026, DOI 10.1016/j.biortech.2026.135499 | 4PET，RESP2(0.5)，Sobtop1.0(dev3.2)。已重新核对本地正文2.9节 | 本地补充DOCX为图表/引物等，未发现嵌入的结构文件或机器可读配体/拓扑包；不排除需向作者索取或其他未核实附件 |
| Berselli et al., ACS Catal. 2025, DOI 10.1021/acscatal.5c01263 | PET4/PEF4：AM1-BCC + GAFF，不属于RESP/RESP2。已核对正文方法 | Zenodo 14697147明确提供拓扑和起始结构。在线ZIP清单实际看到PET4和PEF4分别的system_second.prmtop及system_second.inpcrd |
| Burgin et al., Commun. Chem. 2024, DOI 10.1038/s42004-024-01154-x | PET二聚体，MATCH/CHARMMing生成CGenFF参数，不应归为RESP/RESP2 | 正文公开Zenodo10854763：Amber拓扑、坐标和ATESA输入。此处为整体系文件，不一定有单独配体MOL2 |
| Di Pede-Mattatelli et al., JPCL2026, DOI 10.1021/acs.jpclett.6c00308 | PET4，Gaussian16B.01 HF/6-31G* RESP + GAFF | PLUMED-NEST25.029及作者GitHub公开输入；NEST明确指向.tpr/.gro获取说明。未确认独立ligand.mol2 |
| Temperature-dependent PET binding, RSC Adv.2026, DOI 10.1039/D6RA00343E | PET二聚体，GAMESS-US HF/6-31G(d) RESP + GAFF2 | 方法已确认；独立配体文件披露尚未确认 |

其他本地原文：sc2c04913.pdf（DOI10.1021/acssuschemeng.2c04913）明确使用AM1-BCC，不应归为RESP/RESP2。PCCP2023 D3CP01700A、NewJ.Chem.2024 D3NJ04204A、Chem.Eur.J.2022 chem.202201728 尚未完成配体电荷与可下载文件的逐项审查，本次不强行分类。

公开模型坐标不等于实验晶体配体坐标。以上作者PET2/3/4模型仍需区分实验锚点与计算构建。prmtop/inpcrd中可能可以提取配体坐标、电荷和参数，但应保留原力场上下文；AM1-BCC/CGenFF电荷不能改标签当作RESP。

## 已确认的数据入口

- 2021 SI清单：https://pubs.acs.org/doi/10.1021/acscatal.1c03700
- 2023 JACS及SI：https://pubs.acs.org/doi/10.1021/jacs.3c04427
- 2025正文：https://pubs.acs.org/doi/10.1021/acscatal.5c01263
- 2025数据：https://zenodo.org/records/14697147
- 实际查看的ZIP清单：https://zenodo.org/records/14697147/preview/ZENODO_FILES.zip?include_deleted=0
- 2024正文：https://www.nature.com/articles/s42004-024-01154-x
- 2024数据：https://zenodo.org/records/10854763
- 2026PET4正文：https://pmc.ncbi.nlm.nih.gov/articles/PMC13137247/
- 2026PET4输入：https://www.plumed-nest.org/eggs/25/029/
- 2026二聚体RESP：https://pubs.rsc.org/en/content/articlepdf/2026/ra/d6ra00343e

本地核对源：doc/ja3c04427.pdf、doc/1-s2.0-S0960852426015816-main.pdf、doc/1-s2.0-S0960852426015816-mmc1.docx，以及Jerves2021原文。PDF/DOCX被.gitignore排除，检索应使用rg --files --no-ignore或直接枚举目录；不能以默认rg无输出判断原文件不存在。
