"""
用户注册测试用例执行器
=====================
由 app.py 通过 subprocess 调用。
读取生成的测试用例 Excel，逐条执行验证逻辑，输出测试结果。
"""

import re
import sys
from pathlib import Path
from datetime import datetime

import pandas as pd

# ============================================================
# 配置
# ============================================================
OUTPUT_DIR = Path(__file__).parent / "output"

# 注册字段校验规则
RULES = {
    "username": {
        "min_len": 3,
        "max_len": 20,
        "pattern": re.compile(r"^[a-zA-Z0-9_]+$"),
        "desc": "字母、数字、下划线，3-20 位"
    },
    "email": {
        "pattern": re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"),
        "desc": "标准邮箱格式 xxx@yyy.zzz"
    },
    "password": {
        "min_len": 8,
        "max_len": 20,
        "pattern": re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$"),
        "desc": "8-20 位，至少包含大小写字母和数字"
    },
    "phone": {
        "pattern": re.compile(r"^1[3-9]\d{9}$"),
        "desc": "11 位中国大陆手机号"
    }
}


# ============================================================
# 校验逻辑
# ============================================================

def validate_empty(value) -> bool:
    """检查是否为空（None、空串、'null' 字符串等）。"""
    if value is None:
        return True
    s = str(value).strip()
    if s == "" or s.lower() in ("null", "none", "nan"):
        return True
    return False


def validate_username(value: str) -> str:
    """校验用户名，返回通过（空串）或失败原因。"""
    if validate_empty(value):
        return "用户名为空"
    s = str(value).strip()
    if len(s) < RULES["username"]["min_len"]:
        return f"用户名过短（最小 {RULES['username']['min_len']} 位）"
    if len(s) > RULES["username"]["max_len"]:
        return f"用户名过长（最大 {RULES['username']['max_len']} 位）"
    if not RULES["username"]["pattern"].match(s):
        return f"用户名格式不符（{RULES['username']['desc']}）"
    return ""


def validate_email(value: str) -> str:
    """校验邮箱格式。"""
    if validate_empty(value):
        return "邮箱为空"
    s = str(value).strip()
    if not RULES["email"]["pattern"].match(s):
        return f"邮箱格式不符（{RULES['email']['desc']}）"
    return ""


def validate_password(value: str) -> str:
    """校验密码强度。"""
    if validate_empty(value):
        return "密码为空"
    s = str(value).strip()
    if len(s) < RULES["password"]["min_len"]:
        return f"密码过短（最小 {RULES['password']['min_len']} 位）"
    if len(s) > RULES["password"]["max_len"]:
        return f"密码过长（最大 {RULES['password']['max_len']} 位）"
    if not RULES["password"]["pattern"].match(s):
        return f"密码强度不符（{RULES['password']['desc']}）"
    return ""


def validate_phone(value: str) -> str:
    """校验手机号格式。"""
    if validate_empty(value):
        return "手机号为空"
    s = str(value).strip()
    if not RULES["phone"]["pattern"].match(s):
        return f"手机号格式不符（{RULES['phone']['desc']}）"
    return ""


def validate_confirm_password(password: str, confirm: str) -> str:
    """校验两次密码是否一致。"""
    if validate_empty(confirm):
        return "确认密码为空"
    p = str(password).strip()
    c = str(confirm).strip()
    if p != c:
        return "两次密码输入不一致"
    return ""


def check_security_issues(username: str, email: str, phone: str) -> list[str]:
    """检查安全风险（SQL 注入、XSS 等）。"""
    issues = []
    # SQL 注入检测
    sql_patterns = ["' OR ", "'; --", "DROP ", "DELETE ", "UNION SELECT", "1=1"]
    for field_name, value in [("username", username), ("email", email), ("phone", phone)]:
        for pat in sql_patterns:
            if pat.lower() in str(value).lower():
                issues.append(f"{field_name} 疑似SQL注入: {pat}")
    # XSS 检测
    xss_patterns = ["<script", "javascript:", "onerror=", "onclick="]
    for field_name, value in [("username", username), ("email", email), ("phone", phone)]:
        for pat in xss_patterns:
            if pat.lower() in str(value).lower():
                issues.append(f"{field_name} 疑似XSS攻击: {pat}")
    return issues


# ============================================================
# 测试执行
# ============================================================

def run_one_case(case: dict) -> dict:
    """
    对单条测试用例执行校验逻辑，返回实际结果。

    Args:
        case: 包含各字段值的字典

    Returns:
        {"actual_result": str, "status": "PASS"|"FAIL", "detail": str}
    """
    username = str(case.get("username", ""))
    email = str(case.get("email", ""))
    password = str(case.get("password", ""))
    confirm = str(case.get("confirm_password", ""))
    phone = str(case.get("phone", ""))

    errors = []

    # 逐字段校验
    err = validate_username(username)
    if err:
        errors.append(err)

    err = validate_email(email)
    if err:
        errors.append(err)

    err = validate_password(password)
    if err:
        errors.append(err)

    err = validate_phone(phone)
    if err:
        errors.append(err)

    err = validate_confirm_password(password, confirm)
    if err:
        errors.append(err)

    # 安全检查
    security_issues = check_security_issues(username, email, phone)
    errors.extend(security_issues)

    if errors:
        actual = "注册失败：" + "；".join(errors)
    else:
        actual = "注册成功"

    return {
        "actual_result": actual,
        "status": "PASS",  # 这里判断的是「验证逻辑是否正确执行」，而非用例是否通过
        "detail": ""
    }


def find_latest_excel() -> Path | None:
    """在 output 目录中查找最新的测试用例 Excel。"""
    excel_files = sorted(
        OUTPUT_DIR.glob("testcases*.xlsx"),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )
    return excel_files[0] if excel_files else None


def main():
    """主流程：读取 Excel → 逐条验证 → 输出结果。"""
    # 1. 查找输入文件
    input_file = find_latest_excel()
    if input_file is None:
        print("❌ 未找到测试用例 Excel 文件（output/testcases*.xlsx）")
        sys.exit(1)

    print(f"📂 读取测试用例: {input_file.name}")

    # 2. 读取
    try:
        df = pd.read_excel(input_file, engine="openpyxl")
    except Exception as e:
        print(f"❌ 读取 Excel 失败: {e}")
        sys.exit(1)

    if df.empty:
        print("❌ Excel 文件为空")
        sys.exit(1)

    # 3. 逐条执行
    results = []
    pass_count = 0
    fail_count = 0

    for _, row in df.iterrows():
        case = row.to_dict()
        result = run_one_case(case)

        # 统计：根据预期结果判断
        expected = str(case.get("预期结果", "")).strip()
        actual = result["actual_result"]
        is_expected_pass = "成功" in expected and "失败" not in expected

        if is_expected_pass and "失败" in actual:
            result["status"] = "FAIL"
            result["detail"] = "预期成功但实际失败"
            fail_count += 1
        elif not is_expected_pass and "成功" in actual:
            result["status"] = "FAIL"
            result["detail"] = "预期失败但实际成功"
            fail_count += 1
        else:
            result["status"] = "PASS"
            pass_count += 1

        results.append({
            "用例ID": case.get("用例ID", ""),
            "场景描述": case.get("场景描述", ""),
            "预期结果": expected,
            "实际结果": actual,
            "状态": result["status"],
            "详情": result["detail"]
        })

    # 4. 输出结果 Excel
    result_df = pd.DataFrame(results)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_file = OUTPUT_DIR / f"result_{timestamp}.xlsx"
    result_df.to_excel(result_file, index=False, engine="openpyxl")

    # 5. 打印摘要
    total = len(results)
    print(f"\n{'='*50}")
    print(f"  测试执行完毕")
    print(f"  总计: {total} 条 | ✅ PASS: {pass_count} | ❌ FAIL: {fail_count}")
    print(f"  通过率: {pass_count/total*100:.1f}%")
    print(f"  结果文件: {result_file.name}")
    print(f"{'='*50}\n")

    # 打印失败明细
    if fail_count > 0:
        print("失败用例明细:")
        for r in results:
            if r["状态"] == "FAIL":
                print(f"  [{r['用例ID']}] {r['场景描述']}")
                print(f"    预期: {r['预期结果']}")
                print(f"    实际: {r['实际结果']}")
                print(f"    原因: {r['详情']}")
                print()


if __name__ == "__main__":
    main()
