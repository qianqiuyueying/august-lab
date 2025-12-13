"""
API响应格式规范性属性测试

Feature: personal-website
验证API响应格式规范性和错误处理一致性属性
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from fastapi.testclient import TestClient
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

# 获取认证令牌的辅助函数
def get_auth_token(client):
    """获取有效的认证令牌"""
    response = client.post("/api/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    return response.json()["access_token"]

# 测试数据生成策略
valid_portfolio_data = st.fixed_dictionaries({
    'title': st.text(min_size=1, max_size=200).filter(lambda x: x.strip()),
    'description': st.one_of([st.none(), st.text(max_size=2000)]),
    'tech_stack': st.lists(st.text(min_size=1, max_size=50).filter(lambda x: x.strip()), max_size=10),
    'display_order': st.integers(min_value=0, max_value=9999),
    'is_featured': st.booleans()
})

invalid_portfolio_data = st.one_of([
    # 空标题
    st.fixed_dictionaries({
        'title': st.just(''),
        'description': st.text(max_size=2000),
        'tech_stack': st.lists(st.text(min_size=1, max_size=50), max_size=10),
        'display_order': st.integers(min_value=0, max_value=9999),
        'is_featured': st.booleans()
    }),
    # 超长标题
    st.fixed_dictionaries({
        'title': st.text(min_size=201, max_size=300),
        'description': st.text(max_size=2000),
        'tech_stack': st.lists(st.text(min_size=1, max_size=50), max_size=10),
        'display_order': st.integers(min_value=0, max_value=9999),
        'is_featured': st.booleans()
    }),
    # 无效的显示顺序
    st.fixed_dictionaries({
        'title': st.text(min_size=1, max_size=200),
        'description': st.text(max_size=2000),
        'tech_stack': st.lists(st.text(min_size=1, max_size=50), max_size=10),
        'display_order': st.integers(min_value=-1, max_value=-100),
        'is_featured': st.booleans()
    })
])

class TestAPIResponseFormatCompliance:
    """API响应格式规范性测试"""
    
    def test_property_19_api_response_format_success_responses(self, client):
        """
        Feature: personal-website, Property 19: API响应格式规范性
        验证: 需求 10.1, 10.2
        
        对于任意API请求，响应应该使用标准JSON格式并包含正确的HTTP状态码
        测试成功响应的格式规范性
        """
        # 测试获取作品列表
        response = client.get("/api/portfolio/")
        
        # 验证HTTP状态码
        assert response.status_code == 200
        
        # 验证响应是JSON格式
        assert response.headers["content-type"] == "application/json"
        
        # 验证响应可以解析为JSON
        data = response.json()
        assert isinstance(data, list)
        
        # 验证响应头包含请求ID
        assert "X-Request-ID" in response.headers
        
        # 测试获取个人信息
        response = client.get("/api/profile/")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        
        profile_data = response.json()
        assert isinstance(profile_data, dict)
        assert "id" in profile_data
        assert "name" in profile_data
    
    @given(valid_portfolio_data)
    @settings(max_examples=100)
    def test_property_19_api_response_format_create_success(self, client, portfolio_data):
        """
        Feature: personal-website, Property 19: API响应格式规范性
        验证: 需求 10.1, 10.2
        
        测试创建操作成功响应的格式规范性
        """
        token = get_auth_token(client)
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.post(
            "/api/portfolio/",
            json=portfolio_data,
            headers=headers
        )
        
        # 成功创建应该返回200或201
        assert response.status_code in [200, 201]
        
        # 验证响应格式
        assert response.headers["content-type"] == "application/json"
        
        data = response.json()
        assert isinstance(data, dict)
        
        # 验证返回的数据包含必要字段
        assert "id" in data
        assert "title" in data
        assert "created_at" in data
        assert "updated_at" in data
        
        # 验证数据类型
        assert isinstance(data["id"], int)
        assert isinstance(data["title"], str)
        assert isinstance(data["created_at"], str)
        assert isinstance(data["updated_at"], str)
    
    def test_property_19_api_response_format_not_found_errors(self, client):
        """
        Feature: personal-website, Property 19: API响应格式规范性
        验证: 需求 10.1, 10.2
        
        测试404错误响应的格式规范性
        """
        # 测试获取不存在的作品
        response = client.get("/api/portfolio/99999")
        
        # 验证HTTP状态码
        assert response.status_code == 404
        
        # 验证响应格式
        assert response.headers["content-type"] == "application/json"
        
        data = response.json()
        assert isinstance(data, dict)
        
        # 验证错误响应结构
        assert "error" in data
        error = data["error"]
        
        assert "code" in error
        assert "message" in error
        assert "timestamp" in error
        assert "error_id" in error
        
        # 验证错误信息
        assert error["code"] == "RESOURCE_NOT_FOUND"
        assert "作品" in error["message"]
    
    @given(invalid_portfolio_data)
    @settings(max_examples=100)
    def test_property_19_api_response_format_validation_errors(self, client, invalid_data):
        """
        Feature: personal-website, Property 19: API响应格式规范性
        验证: 需求 10.1, 10.2
        
        测试验证错误响应的格式规范性
        """
        token = get_auth_token(client)
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.post(
            "/api/portfolio/",
            json=invalid_data,
            headers=headers
        )
        
        # 验证HTTP状态码（应该是400或422）
        assert response.status_code in [400, 422]
        
        # 验证响应格式
        assert response.headers["content-type"] == "application/json"
        
        data = response.json()
        assert isinstance(data, dict)
        
        # 验证错误响应结构
        assert "error" in data
        error = data["error"]
        
        assert "code" in error
        assert "message" in error
        assert "timestamp" in error
        assert "error_id" in error
        
        # 验证错误代码
        assert error["code"] in ["VALIDATION_ERROR", "FIELD_VALIDATION_ERROR"]
    
    def test_property_19_api_response_format_authentication_errors(self, client):
        """
        Feature: personal-website, Property 19: API响应格式规范性
        验证: 需求 10.1, 10.2
        
        测试认证错误响应的格式规范性
        """
        # 测试无认证令牌的请求
        response = client.post("/api/portfolio/", json={
            "title": "Test Portfolio",
            "description": "Test description"
        })
        
        # 验证HTTP状态码
        assert response.status_code == 403  # Forbidden
        
        # 验证响应格式
        assert response.headers["content-type"] == "application/json"
        
        data = response.json()
        assert isinstance(data, dict)
        
        # 验证错误响应结构
        assert "error" in data
        error = data["error"]
        
        assert "code" in error
        assert "message" in error
        assert "timestamp" in error
        assert "error_id" in error
        
        # 测试无效认证令牌
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.post("/api/portfolio/", json={
            "title": "Test Portfolio",
            "description": "Test description"
        }, headers=headers)
        
        assert response.status_code == 401
        assert response.headers["content-type"] == "application/json"
    
    def test_property_19_api_response_format_method_not_allowed(self, client):
        """
        Feature: personal-website, Property 19: API响应格式规范性
        验证: 需求 10.1, 10.2
        
        测试方法不允许错误响应的格式规范性
        """
        # 测试不支持的HTTP方法
        response = client.patch("/api/portfolio/")
        
        # 验证HTTP状态码
        assert response.status_code == 405
        
        # 验证响应格式
        assert response.headers["content-type"] == "application/json"
        
        data = response.json()
        assert isinstance(data, dict)
        
        # 验证错误响应结构
        assert "error" in data
        error = data["error"]
        
        assert "code" in error
        assert "message" in error
        assert "timestamp" in error
        assert "error_id" in error
        
        assert error["code"] == "METHOD_NOT_ALLOWED"
    
    def test_property_19_api_response_format_consistency_across_endpoints(self, client):
        """
        Feature: personal-website, Property 19: API响应格式规范性
        验证: 需求 10.1, 10.2
        
        测试不同端点响应格式的一致性
        """
        endpoints_to_test = [
            "/api/portfolio/",
            "/api/blog/",
            "/api/profile/",
        ]
        
        for endpoint in endpoints_to_test:
            response = client.get(endpoint)
            
            # 所有端点都应该返回JSON
            assert response.headers["content-type"] == "application/json"
            
            # 所有响应都应该包含请求ID
            assert "X-Request-ID" in response.headers
            
            # 响应应该可以解析为JSON
            data = response.json()
            assert data is not None
    
    def test_property_19_api_response_format_error_consistency(self, client):
        """
        Feature: personal-website, Property 19: API响应格式规范性
        验证: 需求 10.1, 10.2
        
        测试错误响应格式的一致性
        """
        # 收集不同类型的错误响应
        error_responses = []
        
        # 404错误
        response = client.get("/api/portfolio/99999")
        if response.status_code == 404:
            error_responses.append(response.json())
        
        # 认证错误
        response = client.post("/api/portfolio/", json={"title": "Test"})
        if response.status_code in [401, 403]:
            error_responses.append(response.json())
        
        # 验证所有错误响应都有相同的结构
        for error_response in error_responses:
            assert "error" in error_response
            error = error_response["error"]
            
            # 所有错误都应该有这些字段
            required_fields = ["code", "message", "timestamp", "error_id"]
            for field in required_fields:
                assert field in error, f"错误响应缺少字段: {field}"
            
            # 验证字段类型
            assert isinstance(error["code"], str)
            assert isinstance(error["message"], str)
            assert isinstance(error["timestamp"], str)
            assert isinstance(error["error_id"], str)
    
    def test_property_19_api_response_format_content_type_headers(self, client):
        """
        Feature: personal-website, Property 19: API响应格式规范性
        验证: 需求 10.1, 10.2
        
        测试Content-Type头的正确性
        """
        # 测试各种端点的Content-Type
        test_cases = [
            ("GET", "/api/portfolio/"),
            ("GET", "/api/blog/"),
            ("GET", "/api/profile/"),
            ("GET", "/health"),
        ]
        
        for method, endpoint in test_cases:
            if method == "GET":
                response = client.get(endpoint)
            
            # 所有JSON API响应都应该有正确的Content-Type
            assert "application/json" in response.headers.get("content-type", "")
    
    @given(st.integers(min_value=1, max_value=100))
    @settings(max_examples=100)
    def test_property_19_api_response_format_pagination_consistency(self, client, limit):
        """
        Feature: personal-website, Property 19: API响应格式规范性
        验证: 需求 10.1, 10.2
        
        测试分页响应格式的一致性
        """
        # 测试带分页参数的请求
        response = client.get(f"/api/portfolio/?limit={limit}")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        
        data = response.json()
        assert isinstance(data, list)
        
        # 验证返回的数据量不超过限制
        assert len(data) <= limit
    
    def test_property_20_api_error_handling_consistency(self, client):
        """
        Feature: personal-website, Property 20: API错误处理一致性
        验证: 需求 10.4
        
        对于任意API错误情况，响应应该包含结构化的错误信息和适当的错误代码
        """
        # 测试不同类型的错误是否有一致的处理
        error_test_cases = [
            {
                "description": "资源不存在",
                "request": lambda: client.get("/api/portfolio/99999"),
                "expected_status": 404,
                "expected_error_code": "RESOURCE_NOT_FOUND"
            },
            {
                "description": "认证失败",
                "request": lambda: client.post("/api/portfolio/", json={"title": "Test"}),
                "expected_status": 403,
                "expected_error_code": "FORBIDDEN"
            },
            {
                "description": "方法不允许",
                "request": lambda: client.patch("/api/portfolio/"),
                "expected_status": 405,
                "expected_error_code": "METHOD_NOT_ALLOWED"
            }
        ]
        
        for test_case in error_test_cases:
            response = test_case["request"]()
            
            # 验证状态码
            assert response.status_code == test_case["expected_status"], \
                f"错误类型 '{test_case['description']}' 状态码不正确"
            
            # 验证响应格式
            data = response.json()
            assert "error" in data, f"错误类型 '{test_case['description']}' 缺少error字段"
            
            error = data["error"]
            
            # 验证错误代码
            assert error["code"] == test_case["expected_error_code"], \
                f"错误类型 '{test_case['description']}' 错误代码不正确"
            
            # 验证错误结构一致性
            required_fields = ["code", "message", "timestamp", "error_id"]
            for field in required_fields:
                assert field in error, \
                    f"错误类型 '{test_case['description']}' 缺少字段 {field}"
    
    def test_property_20_api_error_handling_request_id_tracking(self, client):
        """
        Feature: personal-website, Property 20: API错误处理一致性
        验证: 需求 10.4
        
        测试错误响应中的请求ID追踪
        """
        # 发起一个会产生错误的请求
        response = client.get("/api/portfolio/99999")
        
        # 验证响应头包含请求ID
        assert "X-Request-ID" in response.headers
        request_id = response.headers["X-Request-ID"]
        
        # 验证错误响应中也包含请求ID（如果实现了的话）
        data = response.json()
        error = data["error"]
        
        # 请求ID应该在响应头中，错误响应中可能也包含
        assert len(request_id) > 0
        assert isinstance(request_id, str)
    
    def test_property_20_api_error_handling_error_id_uniqueness(self, client):
        """
        Feature: personal-website, Property 20: API错误处理一致性
        验证: 需求 10.4
        
        测试错误ID的唯一性
        """
        error_ids = set()
        
        # 发起多个错误请求
        for i in range(10):
            response = client.get(f"/api/portfolio/9999{i}")
            
            if response.status_code == 404:
                data = response.json()
                error = data["error"]
                error_id = error["error_id"]
                
                # 验证错误ID是唯一的
                assert error_id not in error_ids, f"错误ID重复: {error_id}"
                error_ids.add(error_id)
        
        # 验证收集到了多个唯一的错误ID
        assert len(error_ids) > 0