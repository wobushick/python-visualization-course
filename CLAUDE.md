# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

"基于 LLM 协同辅助自动化测试"课程项目。分两天完成：
- **Day1**: 调用 DeepSeek API 生成登录测试用例 → 输出 Excel/Markdown
- **Day2**: 用 Selenium 对纯 HTML 登录页面执行自动化测试

## 环境与运行

```bash
# 环境激活
conda activate viz-course

# Day1: 生成测试用例（需要 .env 中的 DEEPSEEK_API_KEY）
python test/day1/app.py

# Day2: Selenium 测试（自动启动 HTTP 服务器，有头模式）
cd test/day2/selenium && pytest -v

# 无头模式（CI/服务器）
HEADLESS=1 pytest -v

# 指定外部页面地址（跳过内置 HTTP 服务器）
APP_URL=http://localhost:8080 pytest -v
```

Chrome/ChromeDriver 路径硬编码为 `~/tools/chrome-linux64/` 和 `~/tools/chromedriver-linux64/`，修改 `conftest.py:25-26` 调整。

## 架构

```
test/
├── day1/
│   ├── app.py          # DeepSeek API → Markdown 表格 → Excel（openai SDK + pandas）
│   └── output/         # 生成物：testcases.xlsx, testcases.md
└── day2/
    ├── login.html      # 纯前端登录页（JS 验证，Selenium 测试目标）
    ├── login_page.py   # Gradio 备用登录页（Python 验证，逻辑与 HTML 版一致）
    └── selenium/
        ├── conftest.py     # fixtures: app_url（内置 HTTP 服务器）、driver（Chrome）、result_collector
        └── test_login.py   # parametrize 测试：正常/用户名异常/密码异常/安全/边界值
```

### 关键设计

- **login.html** 的验证逻辑（JS）和 **login_page.py** 的验证逻辑（Python）是同步的——修改验证规则时两边都要改。
- `conftest.py` 中的 `app_url` fixture 会自动在 `127.0.0.1:8080` 启动一个 `http.server` 来 serve `day2/` 目录，端口被占用则跳过。
- `TestResultCollector`（conftest.py）收集每条测试结果，session 结束时写入 `test_results.json`。
- 失败测试自动截图到 `screenshots/` 目录。
- 测试用例硬编码 5 个用户：alice/bob_01/admin/test_user/charlie，与两个登录页面中的 `VALID_USERS` 一致。

### 环境变量

| 变量 | 用途 | 默认值 |
|------|------|--------|
| `DEEPSEEK_API_KEY` | Day1 API 密钥 | 无（必须设置） |
| `DEEPSEEK_BASE_URL` | API 地址 | `https://api.deepseek.com` |
| `DEEPSEEK_MODEL` | 模型名 | `deepseek-v4` |
| `HEADLESS` | Selenium 无头模式 | 未设置=有头 |
| `APP_URL` | 跳过内置服务器，直接访问此地址 | 未设置=自动启动 |

## 注意事项

- `.env` 文件包含 API Key，已 gitignore，不要提交。
- 测试断言用中文关键词：成功=`"通过"`，失败=`"拒绝"`。
- 修改测试用例的 `parametrize` 数据时，确保对应的 `VALID_USERS` 字典也同步更新。
