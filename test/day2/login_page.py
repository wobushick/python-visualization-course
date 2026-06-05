"""
登录页面 — 精致深色主题
========================
用于测试 day1 生成的登录测试用例。
纯前端验证，无需数据库。
"""

import re
from pathlib import Path

import gradio as gr

# ============================================================
# 模拟用户数据库（硬编码）
# ============================================================

VALID_USERS = {
    "alice": "Pass1234",
    "bob_01": "Abcdef1!",
    "admin": "Admin123",
    "test_user": "Test1234",
    "charlie": "Charlie1",
}


# ============================================================
# 登录验证逻辑
# ============================================================

def validate_login(username: str, password: str) -> tuple[str, str]:
    """验证登录信息，返回 (状态, 消息)。"""
    if not username or not username.strip():
        return "✗ 失败", "用户名不能为空"
    if not password or not password.strip():
        return "✗ 失败", "密码不能为空"

    username = username.strip()
    password = password.strip()

    if len(username) < 3:
        return "✗ 失败", "用户名长度不能少于3位"
    if len(username) > 20:
        return "✗ 失败", "用户名长度不能超过20位"
    if not re.match(r"^[a-zA-Z0-9_]+$", username):
        return "✗ 失败", "用户名只能包含字母、数字和下划线"

    if len(password) < 8:
        return "✗ 失败", "密码长度不能少于8位"
    if len(password) > 20:
        return "✗ 失败", "密码长度不能超过20位"
    if not re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$", password):
        return "✗ 失败", "密码必须包含大小写字母和数字"

    sql_patterns = ["' OR ", "'; --", "DROP ", "DELETE ", "UNION SELECT", "1=1"]
    for pat in sql_patterns:
        if pat.lower() in username.lower() or pat.lower() in password.lower():
            return "✗ 失败", "检测到非法输入"

    xss_patterns = ["<script", "javascript:", "onerror=", "onclick="]
    for pat in xss_patterns:
        if pat.lower() in username.lower() or pat.lower() in password.lower():
            return "✗ 失败", "检测到非法输入"

    if username in VALID_USERS:
        if VALID_USERS[username] == password:
            return "✓ 成功", f"欢迎回来，{username}！"
        else:
            return "✗ 失败", "密码错误"
    else:
        return "✗ 失败", "用户不存在"


# ============================================================
# 自定义 CSS
# ============================================================

CUSTOM_CSS = """
/* ── 全局 ── */
.gradio-container {
    background: linear-gradient(135deg, #0f0f0f 0%, #1a1a2e 50%, #16213e 100%) !important;
    min-height: 100vh;
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
}

/* ── 主卡片 ── */
.login-card {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 20px;
    padding: 40px;
    backdrop-filter: blur(20px);
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
    max-width: 480px;
    margin: 0 auto;
}

/* ── 标题区 ── */
.login-header {
    text-align: center;
    margin-bottom: 36px;
}

.login-header h1 {
    color: #f0f0f0 !important;
    font-size: 28px !important;
    font-weight: 600 !important;
    letter-spacing: -0.5px;
    margin-bottom: 8px !important;
}

.login-header p {
    color: #888 !important;
    font-size: 14px !important;
}

/* ── 输入框 ── */
.gr-textbox {
    background: rgba(255, 255, 255, 0.05) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 10px !important;
    transition: all 0.3s ease !important;
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

/* ── 按钮 ── */
.login-btn {
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

.login-btn:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(201, 169, 110, 0.4) !important;
}

.login-btn:active {
    transform: translateY(0) !important;
}

/* ── 输出区 ── */
.output-card {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 16px;
    padding: 24px;
    margin-top: 24px;
}

/* ── 测试账号表格 ── */
.accounts-section {
    margin-top: 32px;
    padding-top: 24px;
    border-top: 1px solid rgba(255, 255, 255, 0.06);
}

.accounts-section h3 {
    color: #888 !important;
    font-size: 12px !important;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 16px !important;
}

.accounts-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
}

.account-chip {
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 13px;
    color: #ccc;
    transition: all 0.2s ease;
}

.account-chip:hover {
    background: rgba(201, 169, 110, 0.1);
    border-color: rgba(201, 169, 110, 0.3);
}

.account-chip code {
    color: #c9a96e;
    font-family: 'SF Mono', 'Fira Code', monospace;
    font-size: 12px;
}

/* ── 响应式 ── */
@media (max-width: 640px) {
    .login-card {
        margin: 16px;
        padding: 24px;
    }
}
"""


# ============================================================
# Gradio 界面
# ============================================================

def create_login_page():
    """构建精致深色主题登录页面。"""
    with gr.Blocks(title="Login") as demo:
        # ── 主卡片 ──
        with gr.Column(elem_classes=["login-card"]):
            # 标题
            gr.HTML("""
                <div class="login-header">
                    <h1>Welcome Back</h1>
                    <p>Enter your credentials to continue</p>
                </div>
            """)

            # 输入区
            username_input = gr.Textbox(
                label="USERNAME",
                placeholder="alice",
                lines=1,
                show_label=True,
            )
            password_input = gr.Textbox(
                label="PASSWORD",
                placeholder="••••••••",
                type="password",
                lines=1,
                show_label=True,
            )

            # 登录按钮
            login_btn = gr.Button("Sign In", elem_classes=["login-btn"])

            # 输出区
            with gr.Column(elem_classes=["output-card"]):
                output_status = gr.Textbox(
                    label="Status",
                    lines=1,
                    interactive=False,
                    show_label=False,
                )
                output_message = gr.Textbox(
                    label="Message",
                    lines=2,
                    interactive=False,
                    show_label=False,
                )

            # 测试账号
            gr.HTML("""
                <div class="accounts-section">
                    <h3>Test Accounts</h3>
                    <div class="accounts-grid">
                        <div class="account-chip"><code>alice</code> / Pass1234</div>
                        <div class="account-chip"><code>bob_01</code> / Abcdef1!</div>
                        <div class="account-chip"><code>admin</code> / Admin123</div>
                        <div class="account-chip"><code>test_user</code> / Test1234</div>
                        <div class="account-chip"><code>charlie</code> / Charlie1</div>
                    </div>
                </div>
            """)

        # ── 事件绑定 ──
        login_btn.click(
            fn=validate_login,
            inputs=[username_input, password_input],
            outputs=[output_status, output_message]
        )
        username_input.submit(
            fn=validate_login,
            inputs=[username_input, password_input],
            outputs=[output_status, output_message]
        )
        password_input.submit(
            fn=validate_login,
            inputs=[username_input, password_input],
            outputs=[output_status, output_message]
        )

    return demo


# ============================================================
# 启动入口
# ============================================================

if __name__ == "__main__":
    demo = create_login_page()
    demo.launch(
        server_port=7862,
        css=CUSTOM_CSS,
        theme=gr.themes.Base(
            primary_hue="amber",
            neutral_hue="slate",
        ).set(
            body_background_fill="transparent",
            body_background_fill_dark="transparent",
        ),
    )
