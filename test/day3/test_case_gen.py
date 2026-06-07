"""
测试用例生成模块
================
从 Day1 提取的核心逻辑，供 Day3 Gradio 应用调用。

提供：
- generate_test_cases(): 调用 DeepSeek API 生成测试用例
- save_to_excel(): 解析 Markdown 表格并保存为 Excel
"""

import re
from pathlib import Path

import pandas as pd
from openai import OpenAI


# ============================================================
# 1. 调用 DeepSeek 生成测试用例
# ============================================================

def generate_test_cases(
    api_key: str,
    base_url: str = "https://api.deepseek.com",
    model: str = "deepseek-chat",
    username_format: str = "用户名，要求字母、数字、下划线，3-20 位",
    password_format: str = "密码，要求 8-20 位，至少包含大小写字母和数字",
    custom_prompt: str | None = None,
) -> str:
    """调用 DeepSeek API 生成 20 条登录测试用例，返回 Markdown 表格。

    custom_prompt: 自定义提示词模板，支持 {username_format} 和 {password_format} 占位符。
                   为 None 时使用内置默认提示词。"""
    if not api_key:
        raise RuntimeError("请先设置 DEEPSEEK_API_KEY")

    if custom_prompt is not None:
        prompt = custom_prompt.format(
            username_format=username_format,
            password_format=password_format,
        )
    else:
        prompt = f"""请根据以下要求生成 30 个用户登录功能测试用例：

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

    client = OpenAI(api_key=api_key, base_url=base_url)
    response = client.chat.completions.create(
        model=model,
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
# 2. 解析 Markdown 表格并保存为 Excel
# ============================================================

def extract_cells(line: str) -> list[str]:
    """从一行 Markdown 表格中提取单元格。"""
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [cell.strip() for cell in line.split("|")]


def save_to_excel(
    markdown_text: str,
    output_dir: Path,
    filename: str = "testcases.xlsx",
) -> str:
    """解析 Markdown 表格并保存为 Excel，返回文件路径。"""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    filepath = str(output_dir / filename)

    lines = [line.strip() for line in markdown_text.strip().split("\n") if line.strip()]

    # 寻找表头行
    header_idx = None
    for i, line in enumerate(lines):
        if "|" in line and any(kw in line for kw in ["用例ID", "username", "password", "预期"]):
            header_idx = i
            break

    if header_idx is None:
        raise RuntimeError("未找到有效的 Markdown 表格")

    headers = extract_cells(lines[header_idx])
    data_start = header_idx + 1
    if data_start < len(lines) and re.match(r"^[\|\s\-:]+$", lines[data_start]):
        data_start += 1

    rows = []
    for line in lines[data_start:]:
        if "|" in line:
            cells = extract_cells(line)
            if len(cells) == len(headers):
                rows.append(cells)

    df = pd.DataFrame(rows, columns=headers)
    df.to_excel(filepath, index=False, engine="openpyxl")
    return filepath
