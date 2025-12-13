"""
前端测试配置文件
"""

import pytest
import os
import sys
import subprocess
import time
import requests


@pytest.fixture(scope="session")
def frontend_server():
    """启动前端开发服务器"""
    # 检查服务器是否已经运行
    try:
        response = requests.get("http://localhost:5173", timeout=2)
        if response.status_code == 200:
            print("前端服务器已在运行")
            yield "http://localhost:5173"
            return
    except requests.exceptions.RequestException:
        pass
    
    # 启动前端服务器
    frontend_dir = os.path.join(os.path.dirname(__file__), "..")
    
    print("启动前端开发服务器...")
    process = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=frontend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # 等待服务器启动
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            response = requests.get("http://localhost:5173", timeout=2)
            if response.status_code == 200:
                print("前端服务器启动成功")
                break
        except requests.exceptions.RequestException:
            time.sleep(1)
    else:
        process.terminate()
        raise Exception("前端服务器启动失败")
    
    yield "http://localhost:5173"
    
    # 清理：终止服务器进程
    process.terminate()
    process.wait()


# Selenium fixtures (only loaded when selenium tests are run)
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    
    @pytest.fixture
    def chrome_driver():
        """创建Chrome WebDriver实例"""
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        
        driver = webdriver.Chrome(options=options)
        
        yield driver
        
        driver.quit()

    @pytest.fixture
    def authenticated_driver(chrome_driver):
        """创建已认证的WebDriver实例"""
        # 设置认证token
        chrome_driver.get("http://localhost:5173")
        chrome_driver.execute_script(
            "localStorage.setItem('admin_token', 'test_token');"
        )
        
        yield chrome_driver

except ImportError:
    # Selenium not available, skip selenium fixtures
    pass


# 测试数据生成器
@pytest.fixture
def test_data():
    """提供测试数据"""
    return {
        "frontend_routes": [
            "/",
            "/portfolio",
            "/blog", 
            "/about"
        ],
        "admin_routes": [
            "/admin",
            "/admin/portfolio",
            "/admin/blog",
            "/admin/profile"
        ],
        "navigation_items": [
            {"name": "首页", "path": "/"},
            {"name": "作品", "path": "/portfolio"},
            {"name": "博客", "path": "/blog"},
            {"name": "关于我", "path": "/about"}
        ]
    }


def pytest_configure(config):
    """pytest配置"""
    # 添加自定义标记
    config.addinivalue_line(
        "markers", "navigation: 导航功能测试"
    )
    config.addinivalue_line(
        "markers", "property: 属性测试"
    )
    config.addinivalue_line(
        "markers", "frontend: 前端测试"
    )


def pytest_collection_modifyitems(config, items):
    """修改测试项配置"""
    for item in items:
        # 为导航测试添加标记
        if "navigation" in item.nodeid:
            item.add_marker(pytest.mark.navigation)
        
        # 为属性测试添加标记
        if "property" in item.nodeid:
            item.add_marker(pytest.mark.property)
        
        # 为前端测试添加标记
        if "frontend" in item.nodeid:
            item.add_marker(pytest.mark.frontend)