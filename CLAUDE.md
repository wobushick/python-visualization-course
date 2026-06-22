# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 环境

```bash
conda activate data-viz  # 从 environment.yml 创建
```

项目根目录在 `/home/ck/python-visualization-course`（WSL2 环境）。

## 项目概述

基于 LLM 协同辅助自动化测试的教学项目。核心流程：使用 DeepSeek API 生成登录测试用例 → 通过 Selenium 对登录页面执行自动化测试 → 收集结果 → pyecharts 可视化。

### 四条工作流

**Day1 — 生成测试用例：**

```bash
python test/day1/app.py
# → 输出 test/day1/output/testcases.xlsx + testcases.md（20 条用例）
```

调用 DeepSeek API（密钥在 `test/day1/.env`），生成 Markdown 表格，解析后写入 Excel。

**Day2 — Selenium 自动化测试：**

```bash
cd test/day2/selenium
pytest -v                       # 有头模式（默认，可见浏览器操作）
HEADLESS=1 pytest -v            # 无头模式（CI/服务器）
```

pytest 自动启动 HTTP 服务器托管 `test/day2/login.html`，然后在 Chrome 中运行 30 条测试用例。结果写入 `test/day2/selenium/test_results.json`，失败时截图保存到 `screenshots/`。

运行单个测试类或特定测试：
```bash
cd test/day2/selenium
pytest -v -k "TestNormalLogin"          # 只运行正常登录
pytest -v -k "bob_01"                   # 运行包含 "bob_01" 的测试
HEADLESS=1 pytest -v -k "TestSecurity"  # 无头模式运行安全测试
```

**Day3 — Gradio 统一平台（端口 7863）：**

```bash
python test/day3/app.py
# → http://127.0.0.1:7863 — 三 Tab 界面
```

集成 Day1 + Day2 为一站式 Web 界面：
- Tab 1「📋 生成测试用例」：可配置格式要求、模型、提示词模板，生成后展示 Markdown + 下载 Excel
- Tab 2「🧪 执行自动化测试」：选择有头/无头模式运行 Selenium，展示结果 DataFrame + 运行日志
- Tab 3「🔑 手动测试登录」：复用 Day2 验证逻辑，点击账号快捷填入

API Key 从 `test/day1/.env` 后台读取，不在 UI 中暴露。

**Day4 — pyecharts 可视化大屏：**

```bash
python test/day4/dashboard.py
# → 输出 test/day4/output/dashboard.html
```

读取 Selenium 测试结果 JSON（优先 `day3/output/` → 回退 `day2/selenium/`），生成 4 张图表：
| # | 类型 | 内容 |
|---|------|------|
| 1 | 饼图（玫瑰图） | 测试输入类型分布 — 按 (用户名, 密码) 特征分 5 类 |
| 2 | 柱状图 | 各类别平均执行耗时 |
| 3 | 水平柱状图 | 验证结果分布 — `actual_output` 归一化为 6 种校验规则 |
| 4 | 堆叠柱状图 | 各类别输入类型构成 — 测试类别 × 输入类型交叉分析 |

Light 主题配色，通过 `Page` 整合为单一 HTML。同时集成到 Day3 Tab 2 的「📊 生成可视化」按钮中（使用 `render_dashboard_embed()` 内嵌到 Gradio）。

图表核心分析逻辑在 `dashboard.py` 中：
- **`_classify_input(username, password)`**：将每条用例按输入特征分为「正常合法」「安全攻击」「边界值」「空值输入」「格式异常」5 类。检查逻辑：先匹配 SQL 注入/XSS 关键词 → 空值 → 首尾空格/长度/特殊字符/密码复杂度。
- **`_normalize_output(actual_output)`**：将原始 `actual_output` 匹配到 6 种归一化校验规则（`VALIDATION_RULES` 字典）：登录成功、格式校验失败、长度校验失败、空值校验失败、账号不匹配、安全拦截。

### 登录页面

有两个版本，验证逻辑相同（5 个硬编码账号，纯前端验证，无数据库）：
- **`test/day2/login.html`** — 纯 HTML/CSS/JS（赛博朋克主题）。Selenium 测试用这个版本。
- **`test/day2/login_page.py`** — Gradio 深色奢华主题（端口 7862）。Day3 的演进起点。

### Chrome 路径

Chrome 和 ChromeDriver 安装在用户目录下：
- Chrome：`~/tools/chrome-linux64/chrome`
- ChromeDriver：`~/tools/chromedriver-linux64/chromedriver`

这两个路径硬编码在 `conftest.py` 中。如需更新 Chrome 版本，替换上述目录即可。

## 项目结构

```
test/
├── day1/                       # Day1: 测试用例生成（CLI）
│   ├── app.py                  # DeepSeek → Markdown → Excel
│   ├── .env                    # API Key（不提交）
│   └── output/
├── day2/                       # Day2: 登录页面 + Selenium 测试
│   ├── login.html              # 赛博朋克主题登录页
│   ├── login_page.py           # Gradio 深色奢华主题
│   └── selenium/
│       ├── conftest.py         # pytest fixtures（driver, app_url, result_collector）
│       ├── test_login.py       # 30 条 parametrized 测试
│       └── test_results.json   # 测试结果 JSON
├── day3/                       # Day3: Gradio 统一平台
│   ├── app.py                  # 三 Tab 主应用（端口 7863）
│   ├── test_case_gen.py        # 用例生成模块（从 Day1 提取）
│   └── output/                 # 生成的用例 + 测试结果副本
└── day4/                       # Day4: pyecharts 可视化大屏
    ├── dashboard.py            # 4 张图表 → HTML
    └── output/
        └── dashboard.html      # 独立可视化大屏
```

## 架构要点

- **`test/day1/app.py`**：独立脚本。通过 `openai` 库调用 DeepSeek（兼容接口），解析返回的 Markdown 表格，用 `openpyxl` 写入 Excel。API 配置从同目录 `.env` 读取。
- **`test/day2/selenium/conftest.py`**：pytest session fixtures。提供 `driver`（全局共享 Chrome 实例，eager 页面加载策略）、`app_url`（自动找可用端口启动 HTTP 服务器）、`wait`（WebDriverWait 封装）、`result_collector`（收集测试结果并在 session 结束时写入 JSON）。
- **`test/day2/selenium/test_login.py`**：30 条 parametrized 测试，分 5 个类 — `TestNormalLogin`（5）、`TestUsernameAbnormal`（7）、`TestPasswordAbnormal`（7）、`TestSecurity`（5）、`TestBoundary`（6）。每个测试记录耗时、截图和实际输出到 `result_collector`。
- **`test/day3/app.py`**：Gradio 三 Tab 界面。Tab 1 调用 `test_case_gen.py` 通过 DeepSeek 生成用例（generator 模式实现加载态）；Tab 2 通过 `subprocess.run("pytest")` 执行 Selenium 测试并解析 `test_results.json`；Tab 3 直接 import Day2 的 `validate_login` 函数。API Key 从 `.env` 后台读取，不暴露在 UI。结果副本存入 `test/day3/output/`。
- **`test/day4/dashboard.py`**：读取 `test_results.json`（优先 `day3/output/` → 回退 `day2/selenium/`），用 pyecharts 生成 4 张图表（Pie/Bar/Bar/Bar），通过 `Page` 整合为独立 HTML，同时提供 `render_dashboard_embed()` 供 Day3 Gradio 嵌入使用。核心分析函数：`_classify_input()` 将输入分为 5 类，`_normalize_output()` 将 `actual_output` 归一化为 6 种校验规则。
- **登录验证规则**（`login.html` JS `validate()` 函数，按执行顺序）：1) trim 后检查空值；2) 用户名长度 3-20；3) 用户名格式 `/^[a-zA-Z0-9_]+$/`；4) 密码长度 8-20；5) 密码必须含大小写字母和数字 `/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$/`；6) SQL 注入关键词检测（`' OR `, `'; --`, `DROP `, `DELETE `, `UNION SELECT`, `1=1`）；7) XSS 模式检测（`<script`, `javascript:`, `onerror=`, `onclick=`）；8) 账号匹配（5 个硬编码账号，比对密码）。注意：空格在步骤 1 被 trim，因此首尾空格被视为空值。

## 关键约定

- `.env` 文件包含真实 API Key，绝不能提交（已在 `.gitignore` 中）。
- `test/.env` 和 `test/day1/.env` 均存在（可能是重复配置，注意保持一致）。
- 输出文件（`output/`、`*.xlsx`、`screenshots/`、`test_results.json`）均在 `.gitignore` 中排除。
- Git 提交信息遵循 `feat:` / `fix:` / `refactor:` / `perf:` / `docs:` 前缀惯例。
- `.claude/settings.local.json` 中有预配置的命令 allowlist。
