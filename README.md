# 基于 LLM 协同辅助自动化测试 — 登录测试用例生成器

基于 DeepSeek API 自动生成登录功能的结构化测试用例，覆盖正常、异常、边界值场景，并支持 Selenium 自动化测试。

## 项目结构

```
├── docs/                       # 课程文档
│   ├── miniconda-guide.md
│   ├── python-environments-explained.md
│   └── 01_基于LLM协同辅助自动化测试--Deepseek V3(1).md
├── test/
│   ├── day1/                   # Day1: 测试用例生成（命令行）
│   │   ├── app.py              # 调用 DeepSeek 生成测试用例 → Excel
│   │   ├── .env                # 你的 API Key（不提交到 git）
│   │   └── output/             # 生成的测试用例和结果
│   └── day2/                   # Day2: 登录页面 + Selenium 测试
│       ├── login.html          # 登录页面（纯 HTML/CSS/JS）
│       ├── login_page.py       # 登录页面（Gradio 备用）
│       └── selenium/
│           ├── conftest.py     # pytest fixtures + HTTP 服务器
│           ├── test_login.py   # Selenium 测试用例
│           └── test_results.json  # 测试结果（JSON）
├── environment.yml             # Conda 环境配置
├── .gitignore
├── .gitattributes
└── README.md
```

## 环境搭建

### 前置条件

- [Miniconda](https://docs.anaconda.com/miniconda/install/) 已安装
- [DeepSeek API Key](https://platform.deepseek.com/) 已获取
- Chrome for Testing（已安装在 `~/tools/chrome-linux64/`）

### Linux / WSL2

```bash
# 1. 克隆项目
git clone <仓库地址>
cd python-visualization-course

# 2. 创建 conda 环境
conda env create -f environment.yml

# 3. 激活环境
conda activate viz-course

# 4. 配置 API Key
cp test/day1/.env.example test/day1/.env
# 编辑 test/day1/.env，填入你的 DeepSeek API Key

# 5. Day1: 生成测试用例
python test/day1/app.py
# → 输出 test/day1/output/testcases.xlsx

# 6. Day2: 运行 Selenium 测试
cd test/day2/selenium
pytest -v
```

### Windows 11

```powershell
# 1. 安装 Miniconda（如未安装）
#    下载地址：https://docs.anaconda.com/miniconda/install/
#    安装时勾选 "Add Miniconda3 to my PATH"

# 2. 打开 Anaconda Prompt（从开始菜单搜索），然后：
git clone <仓库地址>
cd python-visualization-course

# 3. 创建 conda 环境
conda env create -f environment.yml

# 4. 激活环境
conda activate viz-course

# 5. 配置 API Key（在文件资源管理器中操作或命令行）
#    复制 test\day1\.env.example 为 test\day1\.env
#    编辑 .env，填入你的 DeepSeek API Key

# 6. Day1: 生成测试用例
python test\day1\app.py
# → 输出 test\day1\output\testcases.xlsx

# 7. Day2: 运行 Selenium 测试
cd test\day2\selenium
pytest -v
```

> **注意**：`.env` 文件包含你的 API Key，已加入 `.gitignore`，不会被提交到 GitHub。每人需要自己在本地创建。

## 使用说明

### Day1: 生成测试用例

```bash
cd test/day1
python app.py
```

直接运行脚本，调用 DeepSeek API 生成 20 条登录测试用例，输出：
- `output/testcases.xlsx` — Excel 格式
- `output/testcases.md` — Markdown 原文

### Day2: Selenium 自动化测试

```bash
# 直接运行测试（自动启动 HTTP 服务器）
cd test/day2/selenium
pytest -v

# 查看测试结果
cat test_results.json
```

登录页面为纯 HTML，Selenium 测试时会自动启动 HTTP 服务器提供页面。

> **有头模式**：默认以有头模式运行 Chrome，可直观看到浏览器操作。如需无头模式（CI/服务器环境），设置环境变量 `HEADLESS=1`。

## 测试账号

| 用户名 | 密码 |
|--------|------|
| alice | Pass1234 |
| bob_01 | Abcdef1! |
| admin | Admin123 |
| test_user | Test1234 |
| charlie | Charlie1 |

## 协作流程

```bash
# 1. 拉取最新代码
git pull origin main

# 2. 创建自己的分支
git checkout -b feature/你的功能名

# 3. 编写代码...

# 4. 提交
git add .
git commit -m "feat: 做了什么改动"

# 5. 推送
git push origin feature/你的功能名

# 6. 在 GitHub 上创建 Pull Request，组员 review 后合并
```

## 常见问题

**Q: 运行报错 `ModuleNotFoundError: No module named 'xxx'`**
A: 确认已激活 viz-course 环境（终端前面有 `(viz-course)`），如果没有：`conda activate viz-course`

**Q: DeepSeek API 返回错误**
A: 检查 `test/day1/.env` 中的 `DEEPSEEK_API_KEY` 是否正确，以及账户余额是否充足

**Q: Windows 上路径找不到**
A: Windows 路径用 `\` 而非 `/`，如 `python test\day1\app.py`

**Q: Selenium 测试失败**
A: 确保 Chrome for Testing 已安装在 `~/tools/chrome-linux64/`，且登录页面正在运行
