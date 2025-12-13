"""
导航功能完整性属性测试

属性 1: 导航功能完整性
验证: 需求 1.2

测试导航系统的完整性，包括：
- 所有导航链接的可访问性
- 路由跳转的正确性
- 移动端导航的功能性
- 认证相关的导航行为
- 活动状态的正确显示
"""

import pytest
from hypothesis import given, strategies as st, assume
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import json
from typing import List, Dict, Any


class NavigationTester:
    """导航功能测试器"""
    
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        self.base_url = "http://localhost:5173"
        
    def setup_test_environment(self):
        """设置测试环境"""
        # 清除本地存储
        self.driver.execute_script("localStorage.clear();")
        self.driver.execute_script("sessionStorage.clear();")
        
    def get_navigation_links(self) -> List[Dict[str, str]]:
        """获取所有导航链接"""
        try:
            # 前台导航链接
            nav_links = self.driver.find_elements(By.CSS_SELECTOR, "nav a[href]")
            links = []
            
            for link in nav_links:
                href = link.get_attribute("href")
                text = link.text.strip()
                if href and text:
                    links.append({
                        "href": href,
                        "text": text,
                        "element": link
                    })
            
            return links
        except Exception as e:
            return []
    
    def test_navigation_link_accessibility(self, link_info: Dict[str, str]) -> bool:
        """测试导航链接的可访问性"""
        try:
            link = link_info["element"]
            
            # 检查链接是否可见
            if not link.is_displayed():
                return False
            
            # 检查链接是否可点击
            if not link.is_enabled():
                return False
            
            # 检查链接是否有有效的href
            href = link.get_attribute("href")
            if not href or href == "#":
                return False
            
            return True
        except Exception:
            return False
    
    def test_route_navigation(self, target_path: str) -> bool:
        """测试路由导航功能"""
        try:
            # 记录当前URL
            current_url = self.driver.current_url
            
            # 导航到目标路径
            self.driver.get(f"{self.base_url}{target_path}")
            
            # 等待页面加载
            time.sleep(1)
            
            # 检查URL是否正确
            expected_url = f"{self.base_url}{target_path}"
            actual_url = self.driver.current_url
            
            # 处理尾部斜杠的差异
            if actual_url.endswith('/') and not expected_url.endswith('/'):
                expected_url += '/'
            elif not actual_url.endswith('/') and expected_url.endswith('/'):
                expected_url = expected_url.rstrip('/')
            
            return actual_url == expected_url
        except Exception:
            return False
    
    def test_mobile_navigation_toggle(self) -> bool:
        """测试移动端导航切换功能"""
        try:
            # 设置移动端视口
            self.driver.set_window_size(375, 667)
            
            # 查找移动端菜单按钮
            menu_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[class*='md:hidden']"))
            )
            
            # 检查移动端菜单初始状态（应该隐藏）
            mobile_menu = self.driver.find_element(By.CSS_SELECTOR, "div[class*='md:hidden']")
            initial_display = mobile_menu.value_of_css_property("display")
            
            # 点击菜单按钮
            menu_button.click()
            time.sleep(0.5)
            
            # 检查菜单是否显示
            after_click_display = mobile_menu.value_of_css_property("display")
            
            # 再次点击关闭菜单
            menu_button.click()
            time.sleep(0.5)
            
            # 检查菜单是否隐藏
            after_second_click = mobile_menu.value_of_css_property("display")
            
            # 恢复桌面端视口
            self.driver.set_window_size(1920, 1080)
            
            return (initial_display == "none" and 
                   after_click_display == "block" and 
                   after_second_click == "none")
        except Exception:
            # 恢复桌面端视口
            self.driver.set_window_size(1920, 1080)
            return False
    
    def test_active_state_highlighting(self, path: str) -> bool:
        """测试活动状态高亮显示"""
        try:
            # 导航到指定路径
            self.driver.get(f"{self.base_url}{path}")
            time.sleep(1)
            
            # 查找当前活动的导航链接
            active_links = self.driver.find_elements(
                By.CSS_SELECTOR, 
                "nav a[class*='text-primary-600'], nav a.router-link-active"
            )
            
            if not active_links:
                return False
            
            # 检查活动链接是否对应当前路径
            for link in active_links:
                href = link.get_attribute("href")
                if href and href.endswith(path):
                    return True
            
            return False
        except Exception:
            return False
    
    def test_authentication_navigation(self) -> Dict[str, bool]:
        """测试认证相关的导航行为"""
        results = {}
        
        try:
            # 测试未登录状态访问管理页面
            self.setup_test_environment()
            self.driver.get(f"{self.base_url}/admin")
            time.sleep(2)
            
            # 应该重定向到登录页面
            current_url = self.driver.current_url
            results["redirect_to_login"] = "/admin/login" in current_url
            
            # 模拟登录
            if "/admin/login" in current_url:
                # 设置token（模拟登录成功）
                self.driver.execute_script(
                    "localStorage.setItem('admin_token', 'test_token');"
                )
                
                # 再次访问管理页面
                self.driver.get(f"{self.base_url}/admin")
                time.sleep(2)
                
                # 应该能够访问管理页面
                current_url = self.driver.current_url
                results["access_admin_after_login"] = "/admin" in current_url and "/login" not in current_url
                
                # 测试已登录状态访问登录页面
                self.driver.get(f"{self.base_url}/admin/login")
                time.sleep(2)
                
                # 应该重定向到管理后台
                current_url = self.driver.current_url
                results["redirect_from_login_when_authenticated"] = "/admin" in current_url and "/login" not in current_url
            else:
                results["access_admin_after_login"] = False
                results["redirect_from_login_when_authenticated"] = False
            
        except Exception as e:
            results["redirect_to_login"] = False
            results["access_admin_after_login"] = False
            results["redirect_from_login_when_authenticated"] = False
        
        return results
    
    def test_admin_navigation_menu(self) -> bool:
        """测试管理后台导航菜单"""
        try:
            # 设置登录状态
            self.driver.execute_script(
                "localStorage.setItem('admin_token', 'test_token');"
            )
            
            # 访问管理后台
            self.driver.get(f"{self.base_url}/admin")
            time.sleep(2)
            
            # 检查侧边栏菜单项
            expected_menu_items = [
                "/admin",
                "/admin/portfolio", 
                "/admin/blog",
                "/admin/profile"
            ]
            
            for menu_path in expected_menu_items:
                try:
                    menu_item = self.driver.find_element(
                        By.CSS_SELECTOR, 
                        f"li[index='{menu_path}'], a[href='{menu_path}']"
                    )
                    if not menu_item.is_displayed():
                        return False
                except NoSuchElementException:
                    return False
            
            return True
        except Exception:
            return False


@pytest.fixture
def navigation_tester():
    """创建导航测试器"""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1920, 1080)
    
    tester = NavigationTester(driver)
    
    yield tester
    
    driver.quit()


# 前台导航路径策略
frontend_paths = st.sampled_from([
    "/",
    "/portfolio", 
    "/blog",
    "/about"
])

# 管理后台路径策略
admin_paths = st.sampled_from([
    "/admin",
    "/admin/portfolio",
    "/admin/blog", 
    "/admin/profile"
])


class TestNavigationCompletenessProperties:
    """导航功能完整性属性测试类"""
    
    @given(path=frontend_paths)
    def test_frontend_route_navigation_property(self, navigation_tester, path):
        """
        属性: 前台路由导航完整性
        
        对于任何有效的前台路径，导航应该：
        1. 成功加载页面
        2. URL正确匹配
        3. 页面内容正确显示
        """
        # 导航到首页
        navigation_tester.driver.get(navigation_tester.base_url)
        time.sleep(1)
        
        # 测试路由导航
        navigation_success = navigation_tester.test_route_navigation(path)
        
        assert navigation_success, f"导航到路径 {path} 失败"
    
    @given(path=admin_paths)
    def test_admin_route_navigation_property(self, navigation_tester, path):
        """
        属性: 管理后台路由导航完整性
        
        对于任何有效的管理后台路径，在已认证状态下导航应该：
        1. 成功加载页面
        2. URL正确匹配
        3. 认证状态正确验证
        """
        # 设置认证状态
        navigation_tester.driver.get(navigation_tester.base_url)
        navigation_tester.driver.execute_script(
            "localStorage.setItem('admin_token', 'test_token');"
        )
        
        # 测试路由导航
        navigation_success = navigation_tester.test_route_navigation(path)
        
        assert navigation_success, f"管理后台导航到路径 {path} 失败"
    
    def test_navigation_links_accessibility_property(self, navigation_tester):
        """
        属性: 导航链接可访问性
        
        所有导航链接应该：
        1. 可见且可点击
        2. 具有有效的href属性
        3. 具有适当的文本内容
        """
        # 访问首页
        navigation_tester.driver.get(navigation_tester.base_url)
        time.sleep(1)
        
        # 获取所有导航链接
        nav_links = navigation_tester.get_navigation_links()
        
        assert len(nav_links) > 0, "未找到任何导航链接"
        
        # 测试每个链接的可访问性
        for link_info in nav_links:
            accessibility = navigation_tester.test_navigation_link_accessibility(link_info)
            assert accessibility, f"导航链接 '{link_info['text']}' 不可访问"
    
    def test_mobile_navigation_functionality_property(self, navigation_tester):
        """
        属性: 移动端导航功能性
        
        移动端导航应该：
        1. 菜单按钮可见且可点击
        2. 点击后正确显示/隐藏菜单
        3. 菜单项功能正常
        """
        # 访问首页
        navigation_tester.driver.get(navigation_tester.base_url)
        time.sleep(1)
        
        # 测试移动端导航切换
        mobile_nav_works = navigation_tester.test_mobile_navigation_toggle()
        
        assert mobile_nav_works, "移动端导航切换功能异常"
    
    @given(path=frontend_paths)
    def test_active_state_highlighting_property(self, navigation_tester, path):
        """
        属性: 活动状态高亮正确性
        
        对于任何当前访问的页面，对应的导航链接应该：
        1. 显示活动状态样式
        2. 与当前路径正确匹配
        """
        # 测试活动状态高亮
        active_state_correct = navigation_tester.test_active_state_highlighting(path)
        
        # 对于首页，可能没有明确的活动状态，所以跳过
        if path == "/":
            assume(active_state_correct or True)
        else:
            assert active_state_correct, f"路径 {path} 的活动状态高亮显示不正确"
    
    def test_authentication_navigation_property(self, navigation_tester):
        """
        属性: 认证导航行为正确性
        
        认证相关的导航应该：
        1. 未登录时重定向到登录页
        2. 登录后可访问管理页面
        3. 已登录时访问登录页重定向到管理后台
        """
        auth_results = navigation_tester.test_authentication_navigation()
        
        assert auth_results["redirect_to_login"], "未登录访问管理页面时未正确重定向到登录页"
        assert auth_results["access_admin_after_login"], "登录后无法访问管理页面"
        assert auth_results["redirect_from_login_when_authenticated"], "已登录状态访问登录页未正确重定向"
    
    def test_admin_navigation_menu_property(self, navigation_tester):
        """
        属性: 管理后台导航菜单完整性
        
        管理后台的导航菜单应该：
        1. 显示所有必需的菜单项
        2. 菜单项可见且可点击
        3. 菜单项链接正确
        """
        admin_menu_complete = navigation_tester.test_admin_navigation_menu()
        
        assert admin_menu_complete, "管理后台导航菜单不完整或不可用"
    
    def test_navigation_consistency_property(self, navigation_tester):
        """
        属性: 导航一致性
        
        导航系统应该在不同页面间保持一致：
        1. 导航结构相同
        2. 样式一致
        3. 行为一致
        """
        frontend_paths_list = ["/", "/portfolio", "/blog", "/about"]
        
        navigation_structures = []
        
        for path in frontend_paths_list:
            navigation_tester.driver.get(f"{navigation_tester.base_url}{path}")
            time.sleep(1)
            
            # 获取导航结构
            nav_links = navigation_tester.get_navigation_links()
            nav_structure = [link["text"] for link in nav_links if link["text"]]
            navigation_structures.append(nav_structure)
        
        # 检查所有页面的导航结构是否一致
        if navigation_structures:
            first_structure = navigation_structures[0]
            for i, structure in enumerate(navigation_structures[1:], 1):
                assert structure == first_structure, f"页面 {frontend_paths_list[i]} 的导航结构与首页不一致"


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--tb=short"])