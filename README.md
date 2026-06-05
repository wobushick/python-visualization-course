# 基于 LLM 协同辅助自动化测试 — 用户注册测试用例生成器

基于 DeepSeek API + Gradio 构建，自动生成用户注册功能的结构化测试用例，覆盖正常、异常、边界值场景，并支持一键执行验证。

## 项目结构

```
├── docs/                   # 课程文档
│   ├── miniconda-guide.md
│   ├── python-environments-explained.md
│   └── 01_基于LLM协同辅助自动化测试--Deepseek V3(1).md
├── test/
│   ├── app.py              # 主程序：Gradio UI + 用例生成
│   ├── run_tests.py        # 测试执行器：读取 Excel → 逐条校验
│   └── .env                # 你的 API Key（不提交到 git）
├── environment.yml         # Conda 环境配置
├── .gitignore
├── .gitattributes
└── README.md
```

## 环境搭建

### 前置条件

- [Miniconda](https://docs.anaconda.com/miniconda/install/) 已安装
- [DeepSeek API Key](https://platform.deepseek.com/) 已获取

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
cp test/.env.example test/.env
# 编辑 test/.env，填入你的 DeepSeek API Key

# 5. 运行
python test/app.py
# 浏览器打开 http://127.0.0.1:7860
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
#    复制 test\.env.example 为 test\.env
#    编辑 .env，填入你的 DeepSeek API Key

# 6. 运行
python test\app.py
# 浏览器打开 http://127.0.0.1:7860
```

> **注意**：`.env` 文件包含你的 API Key，已加入 `.gitignore`，不会被提交到 GitHub。每人需要自己在本地创建。

## 使用说明

1. 打开 `http://127.0.0.1:7860`
2. 填写各字段格式要求（用户名、邮箱、密码、手机号）
3. 点击 **🔄 生成测试用例** → LLM 自动生成 20 条测试用例并保存为 Excel
4. 审阅生成的用例
5. 点击 **▶️ 执行测试用例** → 对生成的用例逐条验证，输出 PASS/FAIL 结果

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
A: 检查 `test/.env` 中的 `DEEPSEEK_API_KEY` 是否正确，以及账户余额是否充足

**Q: Windows 上路径找不到**
A: Windows 路径用 `\` 而非 `/`，如 `python test\app.py`
