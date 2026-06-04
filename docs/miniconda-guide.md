# Miniconda 使用指南

## 环境概况

| 项目 | 信息 |
|------|------|
| 版本 | conda 26.3.2 |
| 安装路径 | `/home/ck/miniconda3` |
| Python | 3.13.13（base 环境） |
| 默认 channel | `defaults` |

---

## 什么是 Miniconda

Miniconda 是 Anaconda 的精简版，只包含 `conda` 包管理器和 Python 解释器，不附带额外的科学计算包。适合按需安装、节省磁盘空间的场景。

核心概念：
- **环境（environment）**：独立的 Python 运行空间，每个环境的包互不干扰
- **包（package）**：Python 库或工具，通过 `conda` 或 `pip` 安装
- **channel**：包的下载源，类似软件仓库

---

## 环境管理

### 查看环境列表
```bash
conda info --envs
# 或简写
conda env list
```
当前激活的环境前会标 `*`。

### 创建新环境
```bash
# 创建名为 myenv 的环境，指定 Python 版本
conda create -n myenv python=3.12

# 创建时同时安装多个包
conda create -n myenv python=3.12 numpy pandas matplotlib
```

> **推荐**：每个项目使用独立的环境，避免包版本冲突。

### 激活 / 切换环境
```bash
# 激活指定环境
conda activate myenv

# 回到 base 环境
conda activate base
```

### 退出当前环境
```bash
conda deactivate
```

### 删除环境
```bash
conda env remove -n myenv
# 或
conda remove -n myenv --all
```

### 克隆环境
```bash
conda create -n newenv --clone oldenv
```

### 导出 / 导入环境
```bash
# 导出环境配置到文件（方便分享或复现）
conda env export > environment.yml

# 从文件创建环境
conda env create -f environment.yml
```

---

## 包管理

### 安装包
```bash
# 在当前环境中安装
conda install numpy

# 在指定环境中安装
conda install -n myenv numpy pandas

# 安装指定版本
conda install numpy=1.26

# 从指定 channel 安装
conda install -c conda-forge jupyterlab
```

### 查看已安装的包
```bash
# 当前环境所有包
conda list

# 指定环境的包
conda list -n myenv

# 搜索特定包是否安装
conda list | grep numpy
```

### 更新包
```bash
# 更新单个包
conda update numpy

# 更新所有包
conda update --all

# 更新 conda 本身
conda update conda
```

### 删除包
```bash
conda remove numpy
# 从指定环境删除
conda remove -n myenv numpy
```

### 搜索可用包
```bash
conda search numpy
```

---

## Conda vs Pip

| 特性 | conda | pip |
|------|-------|-----|
| 管理范围 | Python 包 + 系统级依赖 | 仅 Python 包 |
| 依赖解析 | 更严格，考虑非 Python 依赖 | 仅 PyPI 层面的依赖 |
| 环境管理 | 内置 | 需配合 venv/virtualenv |
| 可用包数量 | conda-forge 渠道较多 | PyPI 最全 |

**使用原则**：
- 优先用 `conda install`，特别是涉及 C 扩展的包（numpy、scipy 等）
- conda 找不到的包用 `pip install`
- 不要混用 `conda` 和 `pip` 安装同一个包的多个版本，容易出问题

---

## 常用 Channel 推荐

```bash
# 添加 conda-forge（社区维护，包最全的 channel）
conda config --add channels conda-forge

# 设置 channel 优先级为 strict（推荐）
conda config --set channel_priority strict
```

常用的 channel：
- `defaults` — Anaconda 官方（已有）
- `conda-forge` — 社区维护，包最丰富
- `bioconda` — 生物信息学相关包

---

## 日常使用流程示例

```bash
# 1. 为新项目创建环境
conda create -n viz-course python=3.12
conda activate viz-course

# 2. 安装项目需要的包
conda install numpy pandas matplotlib jupyter

# 3. 开始工作
jupyter lab

# 4. 工作结束，退出环境
conda deactivate
```

---

## 清理与维护

```bash
# 清理下载的缓存（释放磁盘空间）
conda clean --all

# 只清理包缓存
conda clean --packages
```

---

## 常见问题

### 找不到包？
```bash
# 试试添加 conda-forge channel 再搜索
conda install -c conda-forge <package_name>
```

### 环境损坏了？
```bash
# 直接删掉重建，成本很低
conda deactivate
conda env remove -n <env_name>
conda create -n <env_name> python=3.12 <需要的包>
```

### 查看 conda 配置
```bash
conda config --show
```

### 查看安装路径
```bash
conda info
```
