# Python 环境解释：到底有几个 Python？

## 一句话回答

你的电脑上有 **两个完全独立的 Python**，它们互不影响：

```
系统 Python     → /usr/bin/python3       (Ubuntu 自带的，3.12.3)
Conda Python    → /home/ck/miniconda3/   (你自己安装的，3.13.13)
```

你终端输入 `python` 时，实际跑的是 **Conda 的**，因为它的路径排在系统路径前面。

---

## 1. 为什么会这样？

Linux 系统（Ubuntu/Debian）本身就需要 Python 来运行一些系统工具。所以装系统时就自带了一个 Python，叫「系统 Python」。

后来你安装了 Miniconda，它又在你的用户目录下装了一套自己的 Python。两套互不干扰。

```bash
# 查看当前用的是哪个 python
which python
# → /home/ck/miniconda3/bin/python    ← Conda 的

# 查看系统 python
/usr/bin/python3 --version
# → Python 3.12.3                     ← 系统的

# 查看 conda python
/home/ck/miniconda3/bin/python --version
# → Python 3.13.13                    ← Conda 的
```

---

## 2. 为什么要用 Conda？系统 Python 不够吗？

系统 Python 有一个限制：**不允许随便 pip install**。这是 Ubuntu 的保护机制（PEP 668），防止你装包时搞坏系统工具。

```bash
# 用系统 pip 装包会报错
pip install gradio
# → error: externally-managed-environment
#    hint: 这个环境被操作系统管着，不让你乱装
```

而 Conda 的 Python 完全由你自己掌控，想装什么装什么，不会影响系统。

---

## 3. 什么是「环境」？

环境就像一个**隔离的房间**。每个房间里有一套 Python + 一堆包，房间之间互不影响。

你当前有两个 conda 环境：

```bash
conda info --envs

# base         /home/ck/miniconda3              ← 默认房间（Python 3.13）
# viz-course   /home/ck/miniconda3/envs/viz-course ← 本项目的房间（Python 3.12）
```

### 为什么要多个环境？

假设你有两个项目：

| 项目 | 需要 numpy | 需要 pandas |
|------|-----------|-------------|
| 项目 A | 1.24 版本 | 2.0 版本 |
| 项目 B | 2.0 版本 | 1.5 版本 |

如果全装在同一个环境里，版本冲突，谁也跑不起来。
用两个独立环境，各装各的，互不打扰。

---

## 4. 日常操作

```bash
# 查看所有环境
conda info --envs

# 激活某个环境（进入那个房间）
conda activate viz-course

# 看看当前在哪个环境
conda info --envs           # 标 * 的就是当前

# 退出当前环境，回到 base
conda deactivate

# 新建一个环境
conda create -n 环境名 python=3.12

# 删掉一个环境
conda env remove -n 环境名
```

### 激活后会怎样？

```bash
ck@machine:~$ conda activate viz-course
(viz-course) ck@machine:~$    # ← 终端前面多了环境名！
```

终端提示符前面出现 `(viz-course)`，说明你已经在那个环境里了。此时输入 `python` 跑的就是 viz-course 里的 Python 3.12。

---

## 5. 你电脑上的实际情况

```
你的电脑
├── 系统 Python 3.12.3 (/usr/bin/python3)
│   └── 系统工具在用，你别动它
│
└── Miniconda (/home/ck/miniconda3/)
    ├── base 环境 (Python 3.13.13)
    │   └── 默认环境，conda 自己用的
    │
    └── viz-course 环境 (Python 3.12.13)
        ├── gradio ✅
        ├── pandas ✅
        ├── openai ✅
        ├── openpyxl ✅
        └── python-dotenv ✅
        └── 本项目专用，已装好所有依赖
```

---

## 6. 本项目怎么跑

```bash
# 1. 进入项目环境
conda activate viz-course

# 2. 确认在正确环境
which python
# → /home/ck/miniconda3/envs/viz-course/bin/python  ← 注意路径里多了 envs/viz-course

# 3. 运行项目
cd /home/ck/python-visualization-course
python test/day1/app.py

# 4. 搞完退出
conda deactivate
```

---

## 7. 常见误解

| 误解 | 实际 |
|------|------|
| "conda base 就是系统 Python" | ❌ 不是。base 是 conda 装的另一个 Python，和系统无关 |
| "pip install 装到哪了" | 取决于你当前在哪个环境。激活 viz-course 后就装到 viz-course 里 |
| "删了 conda 系统 Python 会坏吗" | 不会，系统 Python 完全独立 |
| "环境占很多空间吗" | 还好，一个环境通常几百 MB，Python 本身的基础文件会共享 |

---

## 8. 一句话记住

> **conda 环境 = 独立房间。每个房间有自己的 Python + 包。切换房间用 `conda activate`。和你电脑的系统 Python 没有任何关系。**
