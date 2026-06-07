"""
Day3: LLM 协同辅助自动化测试 — 统一平台
==========================================
使用 Gradio 构建的 Web 界面，集成：
- Tab 1: DeepSeek 测试用例生成（Day1）
- Tab 2: Selenium 自动化测试执行（Day2）
- Tab 3: 手动测试登录页面（Day2）

用法：
    python test/day3/app.py
    → 打开 http://127.0.0.1:7863
"""

import json
import os
import shutil
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

import gradio as gr
import pandas as pd
from dotenv import load_dotenv

# 确保项目根目录在 sys.path 中
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Day3 自己的模块
from test.day3.test_case_gen import generate_test_cases, save_to_excel

# Day2 的登录验证逻辑（Tab 3 复用）
from test.day2.login_page import validate_login

# Day4 的可视化模块（Tab 2 集成）
from test.day4.dashboard import (  # type: ignore
    load_results as load_test_results,
    render_dashboard_embed,
)

# Day4 的可视化模块
from test.day4.dashboard import render_dashboard_embed, load_results as load_dashboard_data

# ============================================================
# 路径配置
# ============================================================

DAY3_DIR = Path(__file__).parent
OUTPUT_DIR = DAY3_DIR / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SELENIUM_DIR = PROJECT_ROOT / "test" / "day2" / "selenium"
RESULTS_FILE = SELENIUM_DIR / "test_results.json"

# 从 day1/.env 读取默认配置（不在 UI 中展示 Key）
load_dotenv(PROJECT_ROOT / "test" / "day1" / ".env")
_ENV_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEFAULT_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEFAULT_MODEL = "deepseek-v4-flash"

DEFAULT_PROMPT = """请根据以下要求生成 30 个用户登录功能测试用例：

### 字段说明：
- username: {username_format}
- password: {password_format}

### 测试用例要求：
1. 包含 5 种正常登录场景（使用符合格式要求的合法数据）
2. 包含 10 种异常场景：
   - 用户名异常（含特殊字符、超长、空值、不存在的用户名、大小写敏感等）
   - 密码不符合要求（过短、纯数字/纯小写/纯大写、空值、错误密码等）
3. 包含 5 种安全测试场景：
   - SQL 注入尝试（用户名、密码、注释符）
   - XSS 攻击尝试（script 标签、javascript 协议）
4. 包含 10 种边界值测试：
   - 用户名长度边界（最短/最长）
   - 密码长度边界（最短/最长）
   - 空格处理（前后空格、中间空格）
   - 特殊字符处理
   - 大小写敏感性测试

### 输出格式要求：
请严格按以下 Markdown 表格格式输出：

| 用例ID | 场景描述 | username | password | 预期结果 |
|--------|---------|----------|----------|----------|
| 1 | xxx | xxx | xxx | 登录成功 |
| 2 | xxx | xxx | xxx | 登录失败：xxx |
...共30行数据"""


# ============================================================
# CSS 主题（继承 Day2 深色奢华风格）
# ============================================================

CUSTOM_CSS = """
/* ── 全局 ── */
.gradio-container {
    background: linear-gradient(135deg, #0f0f0f 0%, #1a1a2e 50%, #16213e 100%) !important;
    min-height: 100vh;
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
}

/* ── Tab 样式 ── */
.tabs > .tab-nav > button {
    color: #888 !important;
    font-weight: 500 !important;
    border-radius: 8px 8px 0 0 !important;
    transition: all 0.3s ease !important;
}
.tabs > .tab-nav > button.selected {
    color: #c9a96e !important;
    border-bottom: 2px solid #c9a96e !important;
}

/* ── 卡片容器 ── */
.card-container {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 28px;
    backdrop-filter: blur(20px);
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
}

/* ── 按钮 ── */
.primary-btn {
    background: linear-gradient(135deg, #c9a96e 0%, #b8944f 100%) !important;
    border: none !important;
    border-radius: 10px !important;
    color: #0f0f0f !important;
    font-weight: 600 !important;
    font-size: 15px !important;
    letter-spacing: 0.3px;
    padding: 12px 24px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(201, 169, 110, 0.3) !important;
}
.primary-btn:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(201, 169, 110, 0.4) !important;
}

.run-btn {
    background: linear-gradient(135deg, #38bdf8 0%, #0ea5e9 100%) !important;
    border: none !important;
    border-radius: 10px !important;
    color: #0f0f0f !important;
    font-weight: 600 !important;
    font-size: 15px !important;
    padding: 12px 24px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(56, 189, 248, 0.3) !important;
}
.run-btn:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(56, 189, 248, 0.4) !important;
}

/* ── 输出区域 ── */
.result-box {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 12px;
    padding: 20px;
    margin-top: 16px;
}

/* ── 输入框 ── */
.gr-textbox {
    background: rgba(255, 255, 255, 0.05) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 10px !important;
}
.gr-textbox:focus-within {
    border-color: #c9a96e !important;
    box-shadow: 0 0 0 3px rgba(201, 169, 110, 0.15) !important;
}
.gr-textbox label {
    color: #aaa !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.gr-textbox input, .gr-textbox textarea {
    color: #f0f0f0 !important;
}
"""


# ============================================================
# Tab 1: 测试用例生成
# ============================================================

def handle_generate(username_format: str, password_format: str,
                    model: str, custom_prompt: str):
    """处理「生成测试用例」按钮点击。使用 generator 实现加载状态。"""
    if not _ENV_API_KEY:
        yield "", None, "⚠️ 请先在 test/day1/.env 中设置 DEEPSEEK_API_KEY"
        return

    yield "", None, "⏳ 正在调用 DeepSeek API，请稍候..."
    try:
        markdown_text = generate_test_cases(
            api_key=_ENV_API_KEY,
            base_url=DEFAULT_BASE_URL,
            model=model,
            username_format=username_format or "用户名，要求字母、数字、下划线，3-20 位",
            password_format=password_format or "密码，要求 8-20 位，至少包含大小写字母和数字",
            custom_prompt=custom_prompt.strip() or None,
        )
        # 保存 Excel
        excel_path = save_to_excel(markdown_text, OUTPUT_DIR, "testcases.xlsx")
        # 同时保存 Markdown
        md_path = OUTPUT_DIR / "testcases.md"
        md_path.write_text(markdown_text, encoding="utf-8")
        yield markdown_text, str(excel_path), f"✅ 用例生成完成 → {excel_path}"
    except Exception as e:
        yield "", None, f"❌ 生成失败: {e}"


# ============================================================
# Tab 2: 执行自动化测试
# ============================================================

def _load_previous_results() -> str:
    """加载已有的测试结果摘要。优先读取 day3/output/ 中的副本。"""
    sources = [OUTPUT_DIR / "test_results.json", RESULTS_FILE]
    for src in sources:
        if src.exists():
            try:
                data = json.loads(src.read_text(encoding="utf-8"))
                run = data.get("test_run", {})
                return (
                    f"📊 上次运行: {run.get('timestamp', 'N/A')}\n"
                    f"总计: {run.get('total', 0)} | ✅ 通过: {run.get('passed', 0)} | "
                    f"❌ 失败: {run.get('failed', 0)}"
                )
            except Exception:
                pass
    return "尚未执行过测试"


def handle_run_tests(headless: bool) -> tuple:
    """通过 subprocess 调用 pytest 执行 Selenium 测试。"""
    try:
        # 准备环境变量
        env = os.environ.copy()
        if headless:
            env["HEADLESS"] = "1"

        # 删除旧结果文件，确保拿到最新结果
        if RESULTS_FILE.exists():
            RESULTS_FILE.unlink()

        start_time = time.time()
        result = subprocess.run(
            ["pytest", "-v", "--tb=short"],
            cwd=str(SELENIUM_DIR),
            capture_output=True, text=True,
            timeout=300,
            env=env,
        )

        elapsed = time.time() - start_time
        stdout = result.stdout[-3000:] if len(result.stdout) > 3000 else result.stdout
        stderr = result.stderr[-1000:] if len(result.stderr) > 1000 else result.stderr

        # 解析结果
        summary_md = f"⏱ 耗时: {elapsed:.1f}s | 退出码: {result.returncode}"

        # 尝试读取 JSON 结果
        if RESULTS_FILE.exists():
            try:
                data = json.loads(RESULTS_FILE.read_text(encoding="utf-8"))
                run = data.get("test_run", {})
                results = data.get("results", [])

                # 保存副本到 day3/output/ 供后续 pyecharts 可视化使用
                day3_results = OUTPUT_DIR / "test_results.json"
                shutil.copy2(RESULTS_FILE, day3_results)

                summary_md = (
                    f"### 📊 测试结果汇总\n"
                    f"- **时间**: {run.get('timestamp', 'N/A')}\n"
                    f"- **总计**: {run.get('total', 0)} | ✅ 通过: {run.get('passed', 0)} | ❌ 失败: {run.get('failed', 0)}\n"
                    f"- **⏱ 耗时**: {elapsed:.1f}s\n"
                    f"- **📁 结果已保存**: `{day3_results}`"
                )

                # 构建 DataFrame — 用 pandas 确保 Gradio 正确渲染
                df_data = []
                for r in results:
                    df_data.append({
                        "用例ID": r.get("test_id", ""),
                        "场景": r.get("name", ""),
                        "分类": r.get("category", ""),
                        "输入": f"{r.get('inputs', {}).get('username', '')} / {r.get('inputs', {}).get('password', '')}",
                        "结果": r.get("status", ""),
                        "输出": r.get("actual_output", "")[:60],
                        "耗时(ms)": r.get("duration_ms", 0),
                    })
                result_df = pd.DataFrame(df_data)

                log_text = f"✅ 测试完成 ({elapsed:.1f}s)\n{stdout[-500:]}"
                return summary_md, result_df, log_text

            except Exception as e:
                summary_md += f"\n⚠️ 解析结果文件失败: {e}"

        # 回退：展示 stdout
        log_text = f"退出码: {result.returncode}\n⏱ {elapsed:.1f}s\n\n{stdout}"
        if stderr:
            log_text += f"\n\nSTDERR:\n{stderr}"
        return summary_md, pd.DataFrame(), log_text

    except subprocess.TimeoutExpired:
        return "❌ 测试执行超时（>5分钟）", pd.DataFrame(), "测试超时，请检查 Chrome 是否正常"
    except Exception as e:
        return f"❌ 执行失败: {e}", pd.DataFrame(), str(e)


def handle_show_dashboard() -> str:
    """生成可视化大屏，返回可嵌入 Gradio 的 HTML。"""
    try:
        results = load_test_results()
        return render_dashboard_embed(results)
    except FileNotFoundError as e:
        return f"""<div style="padding:40px;text-align:center;color:#64748b;">
            <p>⚠️ {e}</p></div>"""
    except Exception as e:
        return f"""<div style="padding:40px;text-align:center;color:#ef4444;">
            <p>❌ 生成失败: {e}</p></div>"""


# ============================================================
# Tab 3: 手动测试登录页
# ============================================================

def handle_open_dashboard() -> str:
    """生成可视化大屏并在浏览器中打开。"""
    try:
        results = load_test_results()
        from test.day4.dashboard import OUTPUT_DIR as DASH_OUTPUT
        dashboard_path = DASH_OUTPUT / "dashboard.html"
        # 确保文件存在
        if not dashboard_path.exists():
            from test.day4.dashboard import build_dashboard
            build_dashboard(results).render(str(dashboard_path))
        webbrowser.open(str(dashboard_path))
        return f"""<div style="padding:20px;text-align:center;color:#16a34a;">
            ✅ 已在浏览器中打开<br><code>{dashboard_path}</code></div>"""
    except Exception as e:
        return f"""<div style="padding:20px;text-align:center;color:#ef4444;">
            ❌ 打开失败: {e}</div>"""


def handle_manual_login(username: str, password: str) -> tuple[str, str]:
    """处理手动登录测试。"""
    status, message = validate_login(username, password)
    return status, message


# ============================================================
# 构建 Gradio 界面
# ============================================================

def build_ui():
    """构建三 Tab Gradio 界面。"""
    with gr.Blocks(title="LLM 协同辅助自动化测试平台") as demo:
        # ── 标题 ──
        gr.Markdown("""
        # 🔐 LLM 协同辅助自动化测试平台
        ### 基于 DeepSeek API · Gradio · Selenium
        ---
        """)

        with gr.Tabs(elem_classes=["tabs"]):

            # ══════════════════════════════════════
            # Tab 1: 生成测试用例
            # ══════════════════════════════════════
            with gr.TabItem("📋 生成测试用例"):
                with gr.Column(elem_classes=["card-container"]):
                    gr.Markdown("### 配置参数")

                    with gr.Row():
                        username_fmt = gr.Textbox(
                            label="用户名格式要求",
                            value="用户名，要求字母、数字、下划线，3-20 位",
                            placeholder="描述用户名的格式约束...",
                            lines=2,
                        )
                        password_fmt = gr.Textbox(
                            label="密码格式要求",
                            value="密码，要求 8-20 位，至少包含大小写字母和数字",
                            placeholder="描述密码的格式约束...",
                            lines=2,
                        )
                        model_select = gr.Dropdown(
                            label="模型",
                            choices=["deepseek-chat", "deepseek-v4-flash"],
                            value=DEFAULT_MODEL,
                        )

                    with gr.Row():
                        prompt_input = gr.Textbox(
                            label="提示词",
                            value=DEFAULT_PROMPT,
                            placeholder="自定义提示词模板，支持 {username_format} 和 {password_format} 占位符...",
                            lines=12,
                            scale=9,
                        )
                        with gr.Column(scale=1, min_width=50):
                            gr.Markdown("")  # spacer
                            reset_prompt_btn = gr.Button("↺ 重置", size="sm")

                    with gr.Row():
                        gen_btn = gr.Button("🚀 生成测试用例", elem_classes=["primary-btn"])

                    gr.Markdown("### 生成结果")
                    output_md = gr.Markdown("", elem_classes=["result-box"])
                    with gr.Row():
                        output_file = gr.File(label="📥 下载 Excel", interactive=False)
                        output_msg = gr.Textbox(label="状态", interactive=False)

                    gen_btn.click(
                        fn=handle_generate,
                        inputs=[username_fmt, password_fmt, model_select, prompt_input],
                        outputs=[output_md, output_file, output_msg],
                    )
                    reset_prompt_btn.click(
                        fn=lambda: DEFAULT_PROMPT,
                        inputs=[],
                        outputs=[prompt_input],
                    )

            # ══════════════════════════════════════
            # Tab 2: 执行自动化测试
            # ══════════════════════════════════════
            with gr.TabItem("🧪 执行自动化测试"):
                with gr.Column(elem_classes=["card-container"]):
                    gr.Markdown("### Selenium 自动化测试")

                    with gr.Row():
                        headless_radio = gr.Radio(
                            label="运行模式",
                            choices=[("有头模式（可见浏览器）", False), ("无头模式（后台运行）", True)],
                            value=False,
                        )
                        gr.Textbox(
                            label="上次运行记录",
                            value=_load_previous_results(),
                            interactive=False,
                            lines=3,
                        )

                    with gr.Row():
                        run_btn = gr.Button("▶️ 执行测试", elem_classes=["run-btn"])

                    gr.Markdown("### 测试结果")
                    result_summary = gr.Markdown("", elem_classes=["result-box"])
                    result_table = gr.DataFrame(
                        label="详细结果",
                        headers=["用例ID", "场景", "分类", "输入", "结果", "输出", "耗时(ms)"],
                        interactive=False,
                    )
                    result_log = gr.Textbox(
                        label="运行日志",
                        lines=8,
                        interactive=False,
                    )

                    run_btn.click(
                        fn=handle_run_tests,
                        inputs=[headless_radio],
                        outputs=[result_summary, result_table, result_log],
                    )

                # 可视化大屏（独立卡片）
                with gr.Column(elem_classes=["card-container"]):
                    gr.Markdown("### 📊 数据可视化大屏")
                    with gr.Row():
                        dashboard_btn = gr.Button("📊 生成可视化", elem_classes=["primary-btn"])
                        open_btn = gr.Button("🔗 在浏览器打开", elem_classes=["run-btn"])
                    dashboard_html = gr.HTML("")

                    dashboard_btn.click(
                        fn=handle_show_dashboard,
                        inputs=[],
                        outputs=[dashboard_html],
                    )
                    open_btn.click(
                        fn=handle_open_dashboard,
                        inputs=[],
                        outputs=[dashboard_html],
                    )

            # ══════════════════════════════════════
            # Tab 3: 手动测试登录页
            # ══════════════════════════════════════
            with gr.TabItem("🔑 手动测试登录"):
                with gr.Column(elem_classes=["card-container"]):
                    gr.Markdown("### 登录验证测试")
                    gr.Markdown("输入用户名和密码，验证登录逻辑——与 Day2 相同的验证规则。")

                    with gr.Row():
                        login_username = gr.Textbox(
                            label="用户名",
                            placeholder="alice",
                            lines=1,
                        )
                        login_password = gr.Textbox(
                            label="密码",
                            type="password",
                            placeholder="••••••••",
                            lines=1,
                        )

                    # 快捷填入测试账号
                    gr.Markdown("*快捷填入：*")
                    with gr.Row():
                        for _user, _pwd in [("alice", "Pass1234"), ("bob_01", "Abcdef1!"),
                                            ("admin", "Admin123"), ("test_user", "Test1234"),
                                            ("charlie", "Charlie1")]:
                            def _make_filler(u=_user, p=_pwd):
                                return lambda: (u, p)
                            chip_btn = gr.Button(f"👤 {_user}", size="sm", scale=1)
                            chip_btn.click(fn=_make_filler(), outputs=[login_username, login_password])

                    with gr.Row():
                        login_btn = gr.Button("🔐 登录", elem_classes=["primary-btn"])

                    with gr.Row():
                        login_status = gr.Textbox(label="状态", interactive=False, lines=1)
                        login_message = gr.Textbox(label="消息", interactive=False, lines=2)

                    login_btn.click(
                        fn=handle_manual_login,
                        inputs=[login_username, login_password],
                        outputs=[login_status, login_message],
                    )
                    login_username.submit(
                        fn=handle_manual_login,
                        inputs=[login_username, login_password],
                        outputs=[login_status, login_message],
                    )
                    login_password.submit(
                        fn=handle_manual_login,
                        inputs=[login_username, login_password],
                        outputs=[login_status, login_message],
                    )

                    gr.Markdown("""
                    ---
                    ### 测试账号

                    | 用户名 | 密码 |
                    |--------|------|
                    | `alice` | `Pass1234` |
                    | `bob_01` | `Abcdef1!` |
                    | `admin` | `Admin123` |
                    | `test_user` | `Test1234` |
                    | `charlie` | `Charlie1` |
                    """)

        return demo


# ============================================================
# 启动入口
# ============================================================

if __name__ == "__main__":
    demo = build_ui()
    demo.launch(
        server_port=7863,
        share=False,
        theme=gr.themes.Base(
            primary_hue="amber",
            neutral_hue="slate",
        ).set(
            body_background_fill="transparent",
            body_background_fill_dark="transparent",
        ),
        css=CUSTOM_CSS,
    )
