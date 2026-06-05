"""
Selenium 测试配置
================
pytest fixtures：浏览器初始化/销毁、Gradio 应用连接、结果收集。
"""

import json
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait

# ============================================================
# 路径配置
# ============================================================

CHROME_PATH = Path.home() / "tools" / "chrome-linux64" / "chrome"
CHROMEDRIVER_PATH = Path.home() / "tools" / "chromedriver-linux64" / "chromedriver"
SCREENSHOTS_DIR = Path(__file__).parent / "screenshots"
RESULTS_FILE = Path(__file__).parent / "test_results.json"
APP_DIR = Path(__file__).parent.parent  # day2/
DEFAULT_PORT = 7861


# ============================================================
# 测试结果收集器
# ============================================================

class TestResultCollector:
    """收集每条测试的结果，最终写入 JSON。"""

    def __init__(self):
        self.results = []
        self.start_time = None
        self.end_time = None

    def add(self, test_id: str, name: str, category: str,
            inputs: dict, status: str, actual_output: str,
            screenshot: str | None = None, duration_ms: int = 0):
        self.results.append({
            "test_id": test_id,
            "name": name,
            "category": category,
            "inputs": inputs,
            "status": status,
            "actual_output": actual_output,
            "screenshot": screenshot,
            "duration_ms": duration_ms,
        })

    def save(self):
        passed = sum(1 for r in self.results if r["status"] == "PASS")
        failed = sum(1 for r in self.results if r["status"] == "FAIL")
        data = {
            "test_run": {
                "timestamp": self.start_time or datetime.now().isoformat(),
                "environment": "WSL2 + Chrome headless",
                "total": len(self.results),
                "passed": passed,
                "failed": failed,
            },
            "results": self.results,
        }
        RESULTS_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2))
        print(f"\n📊 测试结果已保存: {RESULTS_FILE}")
        print(f"   总计: {len(self.results)} | PASS: {passed} | FAIL: {failed}")


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture(scope="session")
def result_collector():
    """Session 级别的结果收集器。"""
    collector = TestResultCollector()
    collector.start_time = datetime.now().isoformat()
    yield collector
    collector.end_time = datetime.now().isoformat()
    collector.save()


@pytest.fixture(scope="session")
def app_url():
    """
    Gradio 应用地址。
    如果 APP_URL 环境变量已设置，直接使用；否则尝试启动 login_page.py。
    """
    env_url = os.environ.get("APP_URL")
    if env_url:
        yield env_url
        return

    # 尝试连接已有实例
    import urllib.request
    try:
        urllib.request.urlopen(f"http://127.0.0.1:{DEFAULT_PORT}", timeout=2)
        yield f"http://127.0.0.1:{DEFAULT_PORT}"
        return
    except Exception:
        pass

    # 启动 Gradio 应用
    proc = subprocess.Popen(
        ["python", str(APP_DIR / "login_page.py")],
        cwd=str(APP_DIR),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    # 等待启动
    for _ in range(30):
        time.sleep(1)
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{DEFAULT_PORT}", timeout=2)
            break
        except Exception:
            continue
    else:
        proc.kill()
        raise RuntimeError("Gradio 应用启动超时")

    yield f"http://127.0.0.1:{DEFAULT_PORT}"
    proc.terminate()
    proc.wait(timeout=5)


@pytest.fixture(scope="function")
def driver(app_url):
    """每个测试函数一个独立的浏览器实例。"""
    SCREENSHOTS_DIR.mkdir(exist_ok=True)

    options = Options()
    options.binary_location = str(CHROME_PATH)
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--lang=zh-CN")

    service = Service(executable_path=str(CHROMEDRIVER_PATH))
    drv = webdriver.Chrome(service=service, options=options)
    drv.implicitly_wait(5)

    drv.get(app_url)
    # 等待 Gradio 页面核心元素加载（最多重试 3 次）
    for attempt in range(3):
        try:
            WebDriverWait(drv, 20).until(
                lambda d: len(d.find_elements("css selector", "textarea, input[type='text']")) >= 2
            )
            break
        except Exception:
            if attempt < 2:
                drv.refresh()
                time.sleep(3)
            else:
                raise

    yield drv
    drv.quit()


@pytest.fixture(scope="function")
def wait(driver):
    """WebDriverWait 封装，默认 10 秒超时。"""
    return WebDriverWait(driver, 10)
