"""
用户注册功能测试用例生成器
==========================
基于 DeepSeek API + Gradio 构建的自动化测试用例生成系统。

与参考文档的区别：
- 测试域从「登录」改为「用户注册」
- 包含更多字段：用户名、邮箱、密码、确认密码、手机号
- 测试场景更丰富：邮箱格式校验、密码强度策略、两次密码一致性、手机号格式等
"""

import os
import re
import subprocess
from pathlib import Path

import gradio as gr
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI

# 自动加载同目录下的 .env 文件
load_dotenv()

# ============================================================
# 配置区
# ============================================================

# DeepSeek API 配置 — Key 写在 .env 文件中，不要写在这里
API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-v4")

# 输出目录
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 1. 大模型客户端
# ============================================================

def get_client():
    """创建 DeepSeek API 客户端。"""
    return OpenAI(api_key=API_KEY, base_url=BASE_URL)


# ============================================================
# 2. 测试用例生成模块
# ============================================================

def generate_test_cases(username_fmt: str, email_fmt: str,
                        password_fmt: str, phone_fmt: str) -> str:
    """
    调用 DeepSeek API 生成用户注册测试用例。

    Args:
        username_fmt:  用户名字段格式要求
        email_fmt:     邮箱字段格式要求
        password_fmt:  密码字段格式要求
        phone_fmt:     手机号字段格式要求

    Returns:
        LLM 返回的 Markdown 格式测试用例文本
    """
    prompt = f"""请根据以下要求生成 20 个用户注册功能测试用例：

### 字段格式要求：
- username: {username_fmt}
- email: {email_fmt}
- password: {password_fmt}
- phone: {phone_fmt}

### 测试用例要求：
1. 包含 5 种正常注册场景（使用符合所有格式要求的合法数据）
2. 包含 10 种异常场景：
   - 用户名异常（含特殊字符、超长、空值、重复用户名等）
   - 邮箱格式错误（缺少@、无效域名、空值等）
   - 密码不符合强度要求（过短、纯数字、空值等）
   - 两次密码输入不一致
   - 手机号格式错误（位数不对、含字母、空值等）
3. 包含 5 种边界值测试：
   - 用户名长度边界（最短/最长）
   - 密码长度边界（最短/最长）
   - 邮箱长度边界
   - 手机号位数边界
   - 特殊字符处理（emoji、SQL注入、XSS等）

### 输出格式要求：
请严格按以下 Markdown 表格格式输出：

| 用例ID | 场景描述 | username | email | password | confirm_password | phone | 预期结果 |
|--------|---------|----------|-------|----------|------------------|-------|----------|
| 1 | xxx | xxx | xxx | xxx | xxx | xxx | 注册成功 |
| 2 | xxx | xxx | xxx | xxx | xxx | xxx | 注册失败：xxx |
...共20行数据
"""

    client = get_client()
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "你是一个专业的测试工程师，擅长生成结构化的测试用例。请严格按照要求的 Markdown 表格格式输出，不要添加额外的解释文字。"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.6
    )
    content = response.choices[0].message.content
    if content is None:
        raise RuntimeError("DeepSeek API 返回内容为空，请重试")
    return content


# ============================================================
# 3. 数据存储模块：Markdown 表格 → Excel
# ============================================================

def save_to_excel(markdown_text: str, filename: str = "testcases.xlsx") -> str:
    """
    从 Markdown 文本中解析表格并保存为 Excel。

    解析策略（多层回退）：
    1. 标准 Markdown 表格（| 表头 | + | --- | + | 数据 |）
    2. 宽松模式：收集所有含 | 的行

    Args:
        markdown_text: 含 Markdown 表格的文本
        filename: 输出文件名

    Returns:
        保存的 Excel 文件路径
    """
    filepath = str(OUTPUT_DIR / filename)

    lines = markdown_text.strip().split("\n")
    lines = [line.strip() for line in lines if line.strip()]

    if not lines:
        return filepath

    # --- 寻找表头行 ---
    header_idx = None
    header_keywords = ["用例ID", "username", "email", "password", "confirm_password", "phone", "预期"]

    for i, line in enumerate(lines):
        if "|" in line and any(kw in line for kw in header_keywords):
            header_idx = i
            break

    if header_idx is None:
        return filepath

    # --- 提取表头 ---
    headers = _extract_cells(lines[header_idx])
    if not headers:
        return filepath

    # --- 跳过分隔行 ---
    data_start = header_idx + 1
    if data_start < len(lines) and re.match(r"^[\|\s\-:]+$", lines[data_start]):
        data_start += 1

    # --- 提取数据行 ---
    rows = []
    for line in lines[data_start:]:
        if "|" in line:
            cells = _extract_cells(line)
            if len(cells) == len(headers):
                rows.append(cells)

    if rows:
        df = pd.DataFrame(rows, columns=headers)
        df.to_excel(filepath, index=False, engine="openpyxl")
        print(f"[保存] {len(rows)} 条用例 → {filepath}")

    return filepath


def _extract_cells(line: str) -> list[str]:
    """从一行 Markdown 表格中提取单元格。"""
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [cell.strip() for cell in line.split("|")]


# ============================================================
# 4. 业务编排：生成 + 保存
# ============================================================

def process_input(username_fmt: str, email_fmt: str,
                  password_fmt: str, phone_fmt: str):
    """
    串联「生成测试用例 → 保存 Excel」流程。

    Returns:
        (Markdown 显示文本, 操作结果消息)
    """
    if not API_KEY or API_KEY == "在此填写你的API-Key":
        return "", "❌ 请先设置 DEEPSEEK_API_KEY 环境变量，或在代码中填写 API Key"

    try:
        # 1. 生成
        markdown_output = generate_test_cases(
            username_fmt, email_fmt, password_fmt, phone_fmt
        )
        # 2. 保存
        excel_path = save_to_excel(markdown_output)
        # 3. 提取纯表格部分用于显示
        table_md = _extract_table_only(markdown_output)
        return table_md, f"✅ 测试用例已保存到 {excel_path}"
    except Exception as e:
        return "", f"❌ 生成失败: {str(e)}"


def _extract_table_only(text: str) -> str:
    """从 LLM 返回中只提取表格部分，方便 Gradio Markdown 渲染。"""
    lines = text.strip().split("\n")
    # 找到第一个 | 和最后一个 | 行
    start = None
    end = None
    for i, line in enumerate(lines):
        if "|" in line and start is None:
            start = i
        if "|" in line:
            end = i
    if start is not None and end is not None:
        return "\n".join(lines[start:end + 1])
    return text


# ============================================================
# 5. 测试执行模块
# ============================================================

def run_test_cases():
    """
    通过 subprocess 调用 run_tests.py 执行测试用例。
    run_tests.py 读取最新生成的 Excel，逐条验证并输出结果。
    """
    runner_script = Path(__file__).parent / "run_tests.py"

    if not runner_script.exists():
        return f"❌ 测试执行脚本不存在: {runner_script}"

    try:
        result = subprocess.run(
            ["python", str(runner_script)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30
        )
        output = result.stdout

        if result.returncode == 0:
            return f"✅ 测试执行完成:\n\n{output}"
        else:
            return f"❌ 测试执行失败 (code={result.returncode}):\n\n{output}\n{result.stderr}"

    except subprocess.TimeoutExpired:
        return "⏱️ 测试执行超时（30秒）"
    except Exception as e:
        return f"❌ 执行测试时发生错误: {str(e)}"


# ============================================================
# 6. Gradio 用户界面
# ============================================================

def create_ui():
    """构建 Gradio 交互界面。"""
    with gr.Blocks(title="用户注册测试用例生成器") as demo:
        gr.Markdown("""
        ## 📝 用户注册测试用例生成器

        基于 **DeepSeek V3** 大模型，自动生成用户注册功能的结构化测试用例。
        输入各字段的格式要求，点击「生成测试用例」即可获得 20 条覆盖正常/异常/边界的测试用例。
        """)

        # ---- 输入区 ----
        gr.Markdown("### 字段格式要求")
        with gr.Row():
            with gr.Column():
                username_input = gr.Textbox(
                    label="用户名 (username)",
                    placeholder="例如：由字母、数字、下划线组成，长度 3-20 位",
                    lines=2
                )
                email_input = gr.Textbox(
                    label="邮箱 (email)",
                    placeholder="例如：符合标准邮箱格式 xxx@yyy.zzz",
                    lines=2
                )
            with gr.Column():
                password_input = gr.Textbox(
                    label="密码 (password)",
                    placeholder="例如：长度 8-20 位，至少包含大小写字母和数字",
                    lines=2
                )
                phone_input = gr.Textbox(
                    label="手机号 (phone)",
                    placeholder="例如：11 位中国大陆手机号",
                    lines=2
                )

        # ---- 按钮 ----
        with gr.Row():
            submit_btn = gr.Button("🔄 生成测试用例", variant="primary")
            run_btn = gr.Button("▶️ 执行测试用例", variant="secondary")

        # ---- 输出区 ----
        gr.Markdown("### 生成结果")
        with gr.Row():
            with gr.Column(scale=2):
                output_table = gr.Markdown(label="生成的测试用例", value="*点击生成按钮查看结果*")
            with gr.Column(scale=1):
                output_msg = gr.Textbox(label="操作日志", lines=10, max_lines=30)

        # ---- 事件绑定 ----
        submit_btn.click(
            fn=process_input,
            inputs=[username_input, email_input, password_input, phone_input],
            outputs=[output_table, output_msg]
        )

        run_btn.click(
            fn=run_test_cases,
            inputs=[],
            outputs=[output_msg]
        )

    return demo


# ============================================================
# 7. 启动入口
# ============================================================

if __name__ == "__main__":
    demo = create_ui()
    demo.launch()
