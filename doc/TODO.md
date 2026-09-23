🔴 P0 — 本周完成
 下载所有较新的 ISPETase PDB
 建立 PDB comparison table
 找 7XTW 及其他 MHET-bound structures
 BLASTP PADFL sequence vs PDB
 确认五个 mutation 的 residue mapping
 搜索是否已有单突变/组合突变 structure
 确定 primary starting PDB
 确定 3-PET 建模方案
 准备 BHET fallback
 安装/准备 PyMOL + ChimeraX + VMD
 建立 WT/PADFL structural comparison figure
🟠 P1 — Structure preparation
 clean PDB
 remove crystallographic artifacts
 add missing residues
 introduce mutations
 build 3-PET
 solvation
 ions
 H++ protonation prediction
 manual catalytic-triad inspection
 minimization
🟡 P1 — Literature
 PADFL original paper + SI
 FAST-PETase JACS
 Jerves PETase QM/MM
 PETase catalytic mechanism
 Funnel MetaD original paper
 FMAP Nature Protocols
 OPES core papers
 Deep-TICA papers
 recent PETase QM/MM work
🟢 P1/P2 — Classical MD
 WT × 3 replicas
 PADFL × 3 replicas
 RMSD/RMSF
 substrate orientation
 Ser–substrate distance
 catalytic-triad H-bonds
 oxyanion-hole H-bonds
 F87–PET distance/dihedral
 loop dynamics
 water network
 contact maps
🔵 P2 — Data-driven sampling
 feature selection
 Deep-TICA
 identify slow modes
 test whether slow modes differ WT/PADFL
 decide OPES/Funnel-OPES setup
 define funnel geometry
 convergence tests
 independent enhanced-sampling replicas
🟣 P3 — QM/MM
 select representative states
 define QM region
 test Gaussian/CP2K
 equilibrate QM/MM
 acylation
 deacylation
 umbrella sampling
 WHAM/PMF
 ΔG‡ comparison
 compare same binding mode vs different binding mode