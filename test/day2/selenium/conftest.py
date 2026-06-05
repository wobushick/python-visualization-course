"""
Selenium 测试配置
================
pytest fixtures：浏览器初始化/销毁、HTTP 服务器、结果收集。
"""

import http.server
import json
import os
import threading
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
DAY2_DIR = Path(__file__).parent.parent  # day2/
DEFAULT_PORT = 8080


# ============================================================
# 测试结果收集器
# ============================================================

class TestResultCollector:
    """收集每条测试的结果，最终写入 JSON。"""

    def __init__(self):
        self.results = []
        self.start_time: str | None = None
        self.end_time: str | None = None

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
                "environment": "WSL2 + Chrome",
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
    启动简易 HTTP 服务器，提供 day2 目录下的 HTML 文件。
    """
    env_url = os.environ.get("APP_URL")
    if env_url:
        yield env_url
        return

    # 直接绑定端口，绑定失败说明被占用则换端口
    class Day2Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(DAY2_DIR), **kwargs)

    port = DEFAULT_PORT
    server = None
    for port in range(DEFAULT_PORT, DEFAULT_PORT + 10):
        try:
            server = http.server.HTTPServer(("127.0.0.1", port), Day2Handler)
            break
        except OSError:
            continue

    if server is None:
        # 所有端口都被占用，尝试连接已有的
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(("127.0.0.1", DEFAULT_PORT))
        sock.close()
        if result == 0:
            yield f"http://127.0.0.1:{DEFAULT_PORT}"
            return
        raise RuntimeError("无法启动 HTTP 服务器：端口被占用且无法连接")

    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{port}"
    server.shutdown()


@pytest.fixture(scope="session")
def driver(app_url):
    """整个测试 session 共享一个浏览器实例。"""
    SCREENSHOTS_DIR.mkdir(exist_ok=True)

    options = Options()
    options.binary_location = str(CHROME_PATH)
    if os.environ.get("HEADLESS"):
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-default-apps")
    options.add_argument("--disable-background-networking")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--lang=zh-CN")
    options.page_load_strategy = "eager"

    service = Service(executable_path=str(CHROMEDRIVER_PATH))
    drv = webdriver.Chrome(service=service, options=options)
    drv.implicitly_wait(5)

    # 首次加载登录页
    drv.get(f"{app_url}/login.html")
    WebDriverWait(drv, 15).until(
        lambda d: d.find_element("css selector", "input[data-testid='username']")
    )

    yield drv
    drv.quit()


@pytest.fixture(scope="session")
def wait(driver):
    """WebDriverWait 封装，默认 10 秒超时。"""
    return WebDriverWait(driver, 10)
