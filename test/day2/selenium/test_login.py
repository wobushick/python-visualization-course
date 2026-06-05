"""
登录页面测试
============
使用 Selenium 测试 day2 的登录页面（HTML 版本）。
"""

import time

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


# ============================================================
# 辅助函数
# ============================================================

# HTML 登录页面元素定位器
USERNAME_INPUT = (By.CSS_SELECTOR, "input[data-testid='username']")
PASSWORD_INPUT = (By.CSS_SELECTOR, "input[data-testid='password']")
BTN_LOGIN = (By.CSS_SELECTOR, "button[type='submit']")
OUTPUT_STATUS = (By.CSS_SELECTOR, ".output .status")
OUTPUT_MESSAGE = (By.CSS_SELECTOR, ".output .message")


def fill_fields(driver, username="", password=""):
    """填写用户名和密码。"""
    u = driver.find_element(*USERNAME_INPUT)
    p = driver.find_element(*PASSWORD_INPUT)
    u.clear()
    if username:
        u.send_keys(username)
    p.clear()
    if password:
        p.send_keys(password)


def click_login(driver, wait):
    """点击登录按钮。"""
    btn = wait.until(EC.element_to_be_clickable(BTN_LOGIN))
    btn.click()


def get_output_text(driver):
    """获取输出区域的状态和消息。"""
    try:
        status = driver.find_element(*OUTPUT_STATUS).text
        message = driver.find_element(*OUTPUT_MESSAGE).text
        return status, message
    except Exception:
        return "", ""


# ============================================================
# 测试用例 - 正常场景
# ============================================================

class TestNormalLogin:
    """正常登录场景。"""

    @pytest.mark.parametrize("username,password,desc", [
        ("alice", "Pass1234", "alice正常登录"),
        ("bob_01", "Abcdef1!", "bob_01正常登录"),
        ("admin", "Admin123", "admin正常登录"),
        ("test_user", "Test1234", "test_user正常登录"),
        ("charlie", "Charlie1", "charlie正常登录"),
    ])
    def test_valid_login(self, driver, wait, result_collector, username, password, desc):
        """合法用户名和密码应能成功登录。"""
        test_id = f"TC_{desc}"
        inputs = {"username": username, "password": password}
        start = time.time()

        try:
            fill_fields(driver, username, password)
            click_login(driver, wait)
            time.sleep(0.5)

            status, message = get_output_text(driver)
            assert "通过" in status, f"登录失败: {message}"

            duration = int((time.time() - start) * 1000)
            result_collector.add(
                test_id=test_id, name=desc, category="正常场景",
                inputs=inputs, status="PASS",
                actual_output=f"登录成功: {message}",
                duration_ms=duration,
            )
        except Exception as e:
            screenshot = _take_screenshot(driver, test_id)
            duration = int((time.time() - start) * 1000)
            result_collector.add(
                test_id=test_id, name=desc, category="正常场景",
                inputs=inputs, status="FAIL",
                actual_output=str(e), screenshot=screenshot,
                duration_ms=duration,
            )
            raise


# ============================================================
# 测试用例 - 用户名异常
# ============================================================

class TestUsernameAbnormal:
    """用户名异常场景。"""

    @pytest.mark.parametrize("username,password,desc", [
        ("ab", "Pass1234", "用户名过短(2位)"),
        ("a" * 21, "Pass1234", "用户名过长(21位)"),
        ("user@name", "Pass1234", "用户名含特殊字符@"),
        ("user name", "Pass1234", "用户名含空格"),
        ("", "Pass1234", "用户名为空"),
        ("notexist", "Pass1234", "不存在的用户名"),
        ("ADMIN", "Admin123", "用户名大小写敏感"),
    ])
    def test_username_abnormal(self, driver, wait, result_collector, username, password, desc):
        """异常用户名应登录失败。"""
        test_id = f"TC_{desc}"
        inputs = {"username": username, "password": password}
        start = time.time()

        try:
            fill_fields(driver, username, password)
            click_login(driver, wait)
            time.sleep(0.5)

            status, message = get_output_text(driver)
            assert "拒绝" in status, f"预期登录失败，但成功了: {message}"

            duration = int((time.time() - start) * 1000)
            result_collector.add(
                test_id=test_id, name=desc, category="用户名异常",
                inputs=inputs, status="PASS",
                actual_output=f"登录失败: {message}",
                duration_ms=duration,
            )
        except Exception as e:
            screenshot = _take_screenshot(driver, test_id)
            duration = int((time.time() - start) * 1000)
            result_collector.add(
                test_id=test_id, name=desc, category="用户名异常",
                inputs=inputs, status="FAIL",
                actual_output=str(e), screenshot=screenshot,
                duration_ms=duration,
            )
            raise


# ============================================================
# 测试用例 - 密码异常
# ============================================================

class TestPasswordAbnormal:
    """密码异常场景。"""

    @pytest.mark.parametrize("username,password,desc", [
        ("alice", "Short1", "密码过短(6位)"),
        ("alice", "12345678", "密码纯数字"),
        ("alice", "abcdefgh", "密码纯小写"),
        ("alice", "ABCDEFGH", "密码纯大写"),
        ("alice", "", "密码为空"),
        ("alice", "WrongPass", "密码错误"),
        ("alice", "a" * 21, "密码过长(21位)"),
    ])
    def test_password_abnormal(self, driver, wait, result_collector, username, password, desc):
        """异常密码应登录失败。"""
        test_id = f"TC_{desc}"
        inputs = {"username": username, "password": password}
        start = time.time()

        try:
            fill_fields(driver, username, password)
            click_login(driver, wait)
            time.sleep(0.5)

            status, message = get_output_text(driver)
            assert "拒绝" in status, f"预期登录失败，但成功了: {message}"

            duration = int((time.time() - start) * 1000)
            result_collector.add(
                test_id=test_id, name=desc, category="密码异常",
                inputs=inputs, status="PASS",
                actual_output=f"登录失败: {message}",
                duration_ms=duration,
            )
        except Exception as e:
            screenshot = _take_screenshot(driver, test_id)
            duration = int((time.time() - start) * 1000)
            result_collector.add(
                test_id=test_id, name=desc, category="密码异常",
                inputs=inputs, status="FAIL",
                actual_output=str(e), screenshot=screenshot,
                duration_ms=duration,
            )
            raise


# ============================================================
# 测试用例 - 安全测试
# ============================================================

class TestSecurity:
    """安全测试场景。"""

    @pytest.mark.parametrize("username,password,desc", [
        ("' OR '1'='1", "Pass1234", "SQL注入_用户名"),
        ("alice", "' OR '1'='1", "SQL注入_密码"),
        ("admin'; --", "Pass1234", "SQL注入_注释"),
        ("<script>alert(1)</script>", "Pass1234", "XSS_script标签"),
        ("alice", "javascript:alert(1)", "XSS_javascript"),
    ])
    def test_security_attacks(self, driver, wait, result_collector, username, password, desc):
        """安全攻击应被检测并拒绝。"""
        test_id = f"TC_{desc}"
        inputs = {"username": username, "password": password}
        start = time.time()

        try:
            fill_fields(driver, username, password)
            click_login(driver, wait)
            time.sleep(0.5)

            status, message = get_output_text(driver)
            assert "拒绝" in status, f"安全攻击被接受了: {message}"

            duration = int((time.time() - start) * 1000)
            result_collector.add(
                test_id=test_id, name=desc, category="安全测试",
                inputs=inputs, status="PASS",
                actual_output=f"安全攻击被拒绝: {message}",
                duration_ms=duration,
            )
        except Exception as e:
            screenshot = _take_screenshot(driver, test_id)
            duration = int((time.time() - start) * 1000)
            result_collector.add(
                test_id=test_id, name=desc, category="安全测试",
                inputs=inputs, status="FAIL",
                actual_output=str(e), screenshot=screenshot,
                duration_ms=duration,
            )
            raise


# ============================================================
# 测试用例 - 边界值
# ============================================================

class TestBoundary:
    """边界值测试场景。"""

    @pytest.mark.parametrize("username,password,desc", [
        ("abc", "Pass1234", "用户名最短(3位)"),
        ("a" * 20, "Pass1234", "用户名最长(20位)"),
        ("alice", "Abcdef1!", "密码最短(8位)"),
        ("alice", "A" + "b" * 18 + "1", "密码最长(20位)"),
        ("alice", "Abcdefg1 ", "密码末尾空格"),
        ("alice", " Abcdefg1", "密码开头空格"),
    ])
    def test_boundary_values(self, driver, wait, result_collector, username, password, desc):
        """边界值测试。"""
        test_id = f"TC_{desc}"
        inputs = {"username": username, "password": password}
        start = time.time()

        try:
            fill_fields(driver, username, password)
            click_login(driver, wait)
            time.sleep(0.5)

            status, message = get_output_text(driver)
            assert "通过" in status or "拒绝" in status, f"异常状态: {status}"

            duration = int((time.time() - start) * 1000)
            result_collector.add(
                test_id=test_id, name=desc, category="边界值",
                inputs=inputs, status="PASS",
                actual_output=f"状态: {status}, 消息: {message}",
                duration_ms=duration,
            )
        except Exception as e:
            screenshot = _take_screenshot(driver, test_id)
            duration = int((time.time() - start) * 1000)
            result_collector.add(
                test_id=test_id, name=desc, category="边界值",
                inputs=inputs, status="FAIL",
                actual_output=str(e), screenshot=screenshot,
                duration_ms=duration,
            )
            raise


# ============================================================
# 截图辅助
# ============================================================

def _take_screenshot(driver, test_id: str) -> str:
    """截图，返回文件路径。"""
    from pathlib import Path
    screenshots_dir = Path(__file__).parent / "screenshots"
    screenshots_dir.mkdir(exist_ok=True)
    # 文件名：测试ID（去掉中文，保留英文和数字）
    safe_name = "".join(c if c.isascii() and c.isalnum() else "_" for c in test_id)
    filepath = screenshots_dir / f"{safe_name}.png"
    driver.save_screenshot(str(filepath))
    return str(filepath)
