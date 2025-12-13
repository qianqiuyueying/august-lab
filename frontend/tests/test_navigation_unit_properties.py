"""
导航功能完整性单元属性测试

属性 1: 导航功能完整性
验证: 需求 1.2

测试导航系统的逻辑完整性，包括：
- 路由配置的正确性
- 导航项目的完整性
- 认证逻辑的正确性
- 路由守卫的功能性
"""

import pytest
from hypothesis import given, strategies as st, assume
from typing import List, Dict, Any, Optional
import json
import re


class NavigationConfig:
    """导航配置类"""
    
    def __init__(self):
        self.frontend_routes = [
            {"path": "/", "name": "Home", "component": "HomePage"},
            {"path": "/portfolio", "name": "Portfolio", "component": "PortfolioPage"},
            {"path": "/portfolio/:id", "name": "PortfolioDetail", "component": "PortfolioDetailPage"},
            {"path": "/blog", "name": "Blog", "component": "BlogPage"},
            {"path": "/blog/:id", "name": "BlogDetail", "component": "BlogDetailPage"},
            {"path": "/about", "name": "About", "component": "AboutPage"}
        ]
        
        self.admin_routes = [
            {"path": "/admin/login", "name": "AdminLogin", "component": "LoginPage", "requiresAuth": False},
            {"path": "/admin", "name": "AdminDashboard", "component": "DashboardPage", "requiresAuth": True},
            {"path": "/admin/portfolio", "name": "AdminPortfolio", "component": "PortfolioManagePage", "requiresAuth": True},
            {"path": "/admin/blog", "name": "AdminBlog", "component": "BlogManagePage", "requiresAuth": True},
            {"path": "/admin/profile", "name": "AdminProfile", "component": "ProfileManagePage", "requiresAuth": True}
        ]
        
        self.navigation_items = [
            {"name": "首页", "path": "/"},
            {"name": "作品", "path": "/portfolio"},
            {"name": "博客", "path": "/blog"},
            {"name": "关于我", "path": "/about"}
        ]
    
    def get_all_routes(self) -> List[Dict[str, Any]]:
        """获取所有路由"""
        return self.frontend_routes + self.admin_routes
    
    def get_public_routes(self) -> List[Dict[str, Any]]:
        """获取公开路由（不需要认证）"""
        return [route for route in self.get_all_routes() 
                if not route.get("requiresAuth", False)]
    
    def get_protected_routes(self) -> List[Dict[str, Any]]:
        """获取受保护路由（需要认证）"""
        return [route for route in self.get_all_routes() 
                if route.get("requiresAuth", False)]
    
    def find_route_by_path(self, path: str) -> Optional[Dict[str, Any]]:
        """根据路径查找路由"""
        for route in self.get_all_routes():
            if route["path"] == path:
                return route
        return None
    
    def is_dynamic_route(self, path: str) -> bool:
        """检查是否为动态路由"""
        return ":" in path
    
    def match_dynamic_route(self, template: str, actual: str) -> bool:
        """匹配动态路由"""
        if not self.is_dynamic_route(template):
            return template == actual
        
        # 将动态路由模板转换为正则表达式
        # 替换 :param 为 ([^/]+)
        pattern = re.sub(r':([^/]+)', r'([^/]+)', template)
        pattern = f"^{pattern}$"
        
        return bool(re.match(pattern, actual))


class AuthenticationManager:
    """认证管理器"""
    
    def __init__(self):
        self.token_key = "admin_token"
    
    def is_authenticated(self, storage: Dict[str, str]) -> bool:
        """检查是否已认证"""
        return self.token_key in storage and storage[self.token_key] is not None
    
    def login(self, storage: Dict[str, str], token: str) -> None:
        """登录"""
        storage[self.token_key] = token
    
    def logout(self, storage: Dict[str, str]) -> None:
        """登出"""
        if self.token_key in storage:
            del storage[self.token_key]


class RouteGuard:
    """路由守卫"""
    
    def __init__(self, nav_config: NavigationConfig, auth_manager: AuthenticationManager):
        self.nav_config = nav_config
        self.auth_manager = auth_manager
    
    def can_access_route(self, path: str, storage: Dict[str, str]) -> bool:
        """检查是否可以访问路由"""
        route = self.nav_config.find_route_by_path(path)
        
        if not route:
            # 检查动态路由
            for r in self.nav_config.get_all_routes():
                if self.nav_config.match_dynamic_route(r["path"], path):
                    route = r
                    break
        
        if not route:
            return False
        
        # 如果路由需要认证，检查认证状态
        if route.get("requiresAuth", False):
            return self.auth_manager.is_authenticated(storage)
        
        return True
    
    def get_redirect_path(self, path: str, storage: Dict[str, str]) -> Optional[str]:
        """获取重定向路径"""
        route = self.nav_config.find_route_by_path(path)
        
        if not route:
            return "/"  # 默认重定向到首页
        
        # 如果访问需要认证的路由但未认证，重定向到登录页
        if route.get("requiresAuth", False) and not self.auth_manager.is_authenticated(storage):
            return "/admin/login"
        
        # 如果已认证用户访问登录页，重定向到管理后台
        if path == "/admin/login" and self.auth_manager.is_authenticated(storage):
            return "/admin"
        
        return None


# 测试策略
valid_paths = st.sampled_from([
    "/", "/portfolio", "/blog", "/about",
    "/admin", "/admin/portfolio", "/admin/blog", "/admin/profile", "/admin/login"
])

dynamic_paths = st.sampled_from([
    "/portfolio/1", "/portfolio/123", "/blog/1", "/blog/abc"
])

invalid_paths = st.sampled_from([
    "/nonexistent", "/admin/nonexistent", "/portfolio/", "/blog/"
])

auth_tokens = st.one_of(
    st.none(),
    st.text(min_size=1, max_size=50)
)


class TestNavigationCompletenessProperties:
    """导航功能完整性属性测试类"""
    
    def create_nav_config(self):
        return NavigationConfig()
    
    def create_auth_manager(self):
        return AuthenticationManager()
    
    def create_route_guard(self):
        nav_config = self.create_nav_config()
        auth_manager = self.create_auth_manager()
        return RouteGuard(nav_config, auth_manager)
    
    def test_navigation_config_completeness_property(self):
        """
        属性: 导航配置完整性
        
        导航配置应该包含所有必需的路由和导航项
        """
        nav_config = self.create_nav_config()
        
        # 检查前台路由完整性
        frontend_paths = [route["path"] for route in nav_config.frontend_routes]
        expected_frontend_paths = ["/", "/portfolio", "/blog", "/about"]
        
        for expected_path in expected_frontend_paths:
            assert expected_path in frontend_paths, f"缺少前台路由: {expected_path}"
        
        # 检查管理后台路由完整性
        admin_paths = [route["path"] for route in nav_config.admin_routes]
        expected_admin_paths = ["/admin", "/admin/login", "/admin/portfolio", "/admin/blog", "/admin/profile"]
        
        for expected_path in expected_admin_paths:
            assert expected_path in admin_paths, f"缺少管理后台路由: {expected_path}"
        
        # 检查导航项完整性
        nav_paths = [item["path"] for item in nav_config.navigation_items]
        for expected_path in expected_frontend_paths:
            assert expected_path in nav_paths, f"缺少导航项: {expected_path}"
    
    def test_route_structure_consistency_property(self):
        """
        属性: 路由结构一致性
        
        所有路由应该具有一致的结构和必需的属性
        """
        nav_config = self.create_nav_config()
        all_routes = nav_config.get_all_routes()
        
        for route in all_routes:
            # 检查必需属性
            assert "path" in route, f"路由缺少path属性: {route}"
            assert "name" in route, f"路由缺少name属性: {route}"
            assert "component" in route, f"路由缺少component属性: {route}"
            
            # 检查属性类型
            assert isinstance(route["path"], str), f"路由path应为字符串: {route}"
            assert isinstance(route["name"], str), f"路由name应为字符串: {route}"
            assert isinstance(route["component"], str), f"路由component应为字符串: {route}"
            
            # 检查路径格式
            assert route["path"].startswith("/"), f"路由路径应以/开头: {route['path']}"
    
    @given(path=valid_paths)
    def test_route_accessibility_property(self, path):
        """
        属性: 路由可访问性
        
        对于任何有效路径，路由守卫应该能够正确判断访问权限
        """
        route_guard = self.create_route_guard()
        
        # 测试未认证状态
        storage_unauthenticated = {}
        can_access = route_guard.can_access_route(path, storage_unauthenticated)
        
        # 测试已认证状态
        storage_authenticated = {"admin_token": "test_token"}
        can_access_auth = route_guard.can_access_route(path, storage_authenticated)
        
        # 管理后台路由（除登录页）需要认证
        if path.startswith("/admin") and path != "/admin/login":
            assert not can_access, f"未认证用户不应能访问 {path}"
            assert can_access_auth, f"已认证用户应能访问 {path}"
        else:
            # 公开路由应该都能访问
            assert can_access, f"公开路由 {path} 应该可访问"
            assert can_access_auth, f"已认证用户应能访问公开路由 {path}"
    
    @given(path=dynamic_paths)
    def test_dynamic_route_matching_property(self, path):
        """
        属性: 动态路由匹配正确性
        
        动态路由应该能够正确匹配相应的路径模式
        """
        nav_config = self.create_nav_config()
        matched = False
        
        for route in nav_config.get_all_routes():
            if nav_config.match_dynamic_route(route["path"], path):
                matched = True
                break
        
        # 检查是否为预期的动态路径
        if path.startswith("/portfolio/") and len(path.split("/")) == 3:
            assert matched, f"动态路径 {path} 应该匹配 /portfolio/:id"
        elif path.startswith("/blog/") and len(path.split("/")) == 3:
            assert matched, f"动态路径 {path} 应该匹配 /blog/:id"
    
    def test_authentication_flow_property(self):
        """
        属性: 认证流程正确性
        
        认证管理器应该正确处理登录/登出流程
        """
        auth_manager = self.create_auth_manager()
        storage = {}
        
        # 初始状态应该未认证
        assert not auth_manager.is_authenticated(storage)
        
        # 登录后应该认证
        auth_manager.login(storage, "test_token")
        assert auth_manager.is_authenticated(storage)
        assert storage["admin_token"] == "test_token"
        
        # 登出后应该未认证
        auth_manager.logout(storage)
        assert not auth_manager.is_authenticated(storage)
        assert "admin_token" not in storage
    
    @given(token=auth_tokens)
    def test_authentication_state_consistency_property(self, token):
        """
        属性: 认证状态一致性
        
        认证状态应该与存储的token保持一致
        """
        auth_manager = self.create_auth_manager()
        storage = {}
        
        if token is not None:
            storage["admin_token"] = token
            expected_auth = True
        else:
            expected_auth = False
        
        actual_auth = auth_manager.is_authenticated(storage)
        assert actual_auth == expected_auth, f"认证状态不一致: token={token}, expected={expected_auth}, actual={actual_auth}"
    
    def test_route_guard_redirect_logic_property(self):
        """
        属性: 路由守卫重定向逻辑正确性
        
        路由守卫应该根据认证状态正确处理重定向
        """
        route_guard = self.create_route_guard()
        
        # 测试未认证访问管理页面
        storage_unauth = {}
        redirect = route_guard.get_redirect_path("/admin", storage_unauth)
        assert redirect == "/admin/login", "未认证访问管理页面应重定向到登录页"
        
        # 测试已认证访问登录页
        storage_auth = {"admin_token": "test_token"}
        redirect = route_guard.get_redirect_path("/admin/login", storage_auth)
        assert redirect == "/admin", "已认证访问登录页应重定向到管理后台"
        
        # 测试正常访问
        redirect = route_guard.get_redirect_path("/", storage_unauth)
        assert redirect is None, "正常访问不应重定向"
        
        redirect = route_guard.get_redirect_path("/admin", storage_auth)
        assert redirect is None, "已认证访问管理页面不应重定向"
    
    def test_navigation_items_route_mapping_property(self):
        """
        属性: 导航项与路由映射正确性
        
        所有导航项应该对应有效的路由
        """
        nav_config = self.create_nav_config()
        all_route_paths = [route["path"] for route in nav_config.get_all_routes()]
        
        for nav_item in nav_config.navigation_items:
            nav_path = nav_item["path"]
            assert nav_path in all_route_paths, f"导航项路径 {nav_path} 没有对应的路由"
    
    def test_route_name_uniqueness_property(self):
        """
        属性: 路由名称唯一性
        
        所有路由名称应该是唯一的
        """
        nav_config = self.create_nav_config()
        all_routes = nav_config.get_all_routes()
        route_names = [route["name"] for route in all_routes]
        
        # 检查名称唯一性
        unique_names = set(route_names)
        assert len(route_names) == len(unique_names), f"路由名称不唯一: {route_names}"
    
    def test_protected_routes_authentication_requirement_property(self):
        """
        属性: 受保护路由认证要求正确性
        
        所有管理后台路由（除登录页）都应该要求认证
        """
        nav_config = self.create_nav_config()
        admin_routes = [route for route in nav_config.admin_routes if route["path"] != "/admin/login"]
        
        for route in admin_routes:
            assert route.get("requiresAuth", False), f"管理后台路由 {route['path']} 应该要求认证"
        
        # 登录页不应要求认证
        login_route = nav_config.find_route_by_path("/admin/login")
        assert not login_route.get("requiresAuth", False), "登录页不应要求认证"
    
    @given(path=invalid_paths)
    def test_invalid_route_handling_property(self, path):
        """
        属性: 无效路由处理正确性
        
        对于无效路径，系统应该正确处理（拒绝访问或重定向）
        """
        route_guard = self.create_route_guard()
        storage = {}
        can_access = route_guard.can_access_route(path, storage)
        
        # 无效路径应该不能访问
        assert not can_access, f"无效路径 {path} 不应该可访问"


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--tb=short"])