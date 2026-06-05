"""
简单登录页面
============
用于测试 day1 生成的登录测试用例。
纯前端验证，无需数据库。
"""

import re
from pathlib import Path

import gradio as gr

# ============================================================
# 模拟用户数据库（硬编码）
# ============================================================

# 模拟的合法用户
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
    """
    验证登录信息。

    Args:
        username: 用户名
        password: 密码

    Returns:
        (状态, 消息)
    """
    # 1. 空值检查
    if not username or not username.strip():
        return "❌ 失败", "用户名不能为空"
    if not password or not password.strip():
        return "❌ 失败", "密码不能为空"

    username = username.strip()
    password = password.strip()

    # 2. 用户名格式校验
    if len(username) < 3:
        return "❌ 失败", "用户名长度不能少于3位"
    if len(username) > 20:
        return "❌ 失败", "用户名长度不能超过20位"
    if not re.match(r"^[a-zA-Z0-9_]+$", username):
        return "❌ 失败", "用户名只能包含字母、数字和下划线"

    # 3. 密码格式校验
    if len(password) < 8:
        return "❌ 失败", "密码长度不能少于8位"
    if len(password) > 20:
        return "❌ 失败", "密码长度不能超过20位"
    if not re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$", password):
        return "❌ 失败", "密码必须包含大小写字母和数字"

    # 4. SQL 注入检测
    sql_patterns = ["' OR ", "'; --", "DROP ", "DELETE ", "UNION SELECT", "1=1"]
    for pat in sql_patterns:
        if pat.lower() in username.lower() or pat.lower() in password.lower():
            return "❌ 失败", "检测到非法输入"

    # 5. XSS 检测
    xss_patterns = ["<script", "javascript:", "onerror=", "onclick="]
    for pat in xss_patterns:
        if pat.lower() in username.lower() or pat.lower() in password.lower():
            return "❌ 失败", "检测到非法输入"

    # 6. 用户名和密码匹配检查
    if username in VALID_USERS:
        if VALID_USERS[username] == password:
            return "✅ 成功", f"欢迎回来，{username}！"
        else:
            return "❌ 失败", "密码错误"
    else:
        return "❌ 失败", "用户不存在"


# ============================================================
# Gradio 界面
# ============================================================

def create_login_page():
    """构建登录页面。"""
    with gr.Blocks(title="简单登录页面") as demo:
        gr.Markdown("""
        ## 🔐 简单登录页面

        用于测试登录功能的简单页面，纯前端验证，无需数据库。

        **测试账号：**
        | 用户名 | 密码 |
        |--------|------|
        | alice | Pass1234 |
        | bob_01 | Abcdef1! |
        | admin | Admin123 |
        | test_user | Test1234 |
        | charlie | Charlie1 |
        """)

        with gr.Row():
            with gr.Column(scale=1):
                username_input = gr.Textbox(
                    label="用户名",
                    placeholder="请输入用户名",
                    lines=1
                )
                password_input = gr.Textbox(
                    label="密码",
                    placeholder="请输入密码",
                    type="password",
                    lines=1
                )
                login_btn = gr.Button("登录", variant="primary")

            with gr.Column(scale=1):
                output_status = gr.Textbox(label="状态", lines=1)
                output_message = gr.Textbox(label="消息", lines=3)

        # 事件绑定
        login_btn.click(
            fn=validate_login,
            inputs=[username_input, password_input],
            outputs=[output_status, output_message]
        )

        # 支持回车登录
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
    demo.launch(server_port=7861)
