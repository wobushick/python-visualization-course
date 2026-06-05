"""
登录功能测试用例生成器
======================
基于 DeepSeek API，直接运行生成登录测试用例并保存到本地 Excel。

用法：
    python app.py
"""

import os
import re
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI

# 自动加载同目录下的 .env 文件
load_dotenv()

# ============================================================
# 配置区
# ============================================================

API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-v4")

OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 1. 调用 DeepSeek 生成测试用例
# ============================================================

def generate_test_cases() -> str:
    """调用 DeepSeek API 生成 20 条登录测试用例，返回 Markdown 表格。"""
    if not API_KEY:
        raise RuntimeError("请先在 .env 文件中设置 DEEPSEEK_API_KEY")

    prompt = """请根据以下要求生成 20 个用户登录功能测试用例：

### 字段说明：
- username: 用户名，要求字母、数字、下划线，3-20 位
- password: 密码，要求 8-20 位，至少包含大小写字母和数字

### 测试用例要求：
1. 包含 5 种正常登录场景（使用符合格式要求的合法数据）
2. 包含 10 种异常场景：
   - 用户名异常（含特殊字符、超长、空值、不存在的用户名等）
   - 密码不符合要求（过短、纯数字、空值、错误密码等）
   - 用户名和密码组合错误
   - SQL 注入尝试
   - XSS 攻击尝试
3. 包含 5 种边界值测试：
   - 用户名长度边界（最短/最长）
   - 密码长度边界（最短/最长）
   - 特殊字符处理（emoji、SQL注入、XSS等）
   - 空格处理（前后空格、中间空格）
   - 大小写敏感性测试

### 输出格式要求：
请严格按以下 Markdown 表格格式输出：

| 用例ID | 场景描述 | username | password | 预期结果 |
|--------|---------|----------|----------|----------|
| 1 | xxx | xxx | xxx | 登录成功 |
| 2 | xxx | xxx | xxx | 登录失败：xxx |
...共20行数据"""

    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
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


def save_to_excel(markdown_text: str, filename: str = "testcases.xlsx") -> str:
    """解析 Markdown 表格并保存为 Excel，返回文件路径。"""
    filepath = str(OUTPUT_DIR / filename)
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


# ============================================================
# 3. 主流程
# ============================================================

if __name__ == "__main__":
    print("🔄 正在调用 DeepSeek 生成登录测试用例...")
    md = generate_test_cases()
    print("✅ 用例生成完成")

    path = save_to_excel(md)
    print(f"📁 已保存到 {path}")

    # 同时保存原始 Markdown
    md_path = OUTPUT_DIR / "testcases.md"
    md_path.write_text(md, encoding="utf-8")
    print(f"📁 Markdown 原文 → {md_path}")
