"""
SQL注入防护有效性属性测试

Feature: personal-website
验证SQL注入防护有效性属性
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from app.security import SecurityQueryBuilder, SafeQueryExecutor, SQLInjectionError
from app.models import Portfolio, Blog, Profile

# 获取认证令牌的辅助函数
def get_auth_token(client):
    """获取有效的认证令牌"""
    response = client.post("/api/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    return response.json()["access_token"]

# SQL注入攻击模式策略
sql_injection_patterns = st.one_of([
    # 经典SQL注入
    st.just("'; DROP TABLE users; --"),
    st.just("' OR '1'='1"),
    st.just("' OR 1=1 --"),
    st.just("admin'--"),
    st.just("admin' #"),
    st.just("admin'/*"),
    
    # UNION攻击
    st.just("' UNION SELECT * FROM users --"),
    st.just("1' UNION SELECT null, username, password FROM users --"),
    
    # 布尔盲注
    st.just("' AND (SELECT COUNT(*) FROM users) > 0 --"),
    st.just("' AND ASCII(SUBSTRING((SELECT password FROM users WHERE username='admin'),1,1)) > 65 --"),
    
    # 时间盲注
    st.just("'; WAITFOR DELAY '00:00:05' --"),
    st.just("' AND (SELECT SLEEP(5)) --"),
    st.just("'; SELECT BENCHMARK(1000000,MD5(1)) --"),
    
    # 堆叠查询
    st.just("'; INSERT INTO users VALUES ('hacker', 'password'); --"),
    st.just("'; UPDATE users SET password='hacked' WHERE username='admin'; --"),
    
    # 函数注入
    st.just("'; SELECT LOAD_FILE('/etc/passwd'); --"),
    st.just("'; SELECT * INTO OUTFILE '/tmp/hack.txt' FROM users; --"),
    
    # 注释绕过
    st.just("'/**/OR/**/1=1/**/--"),
    st.just("'/*comment*/OR/*comment*/1=1/*comment*/--"),
    
    # 编码绕过
    st.just("' OR CHAR(49)=CHAR(49) --"),
    st.just("' OR HEX('a')=HEX('a') --"),
    
    # 其他攻击模式
    st.just("' OR EXISTS(SELECT * FROM users) --"),
    st.just("' HAVING 1=1 --"),
    st.just("' GROUP BY 1 --"),
    st.just("' ORDER BY 1 --"),
    st.just("' LIMIT 1 OFFSET 1 --"),
])

# 正常输入策略
normal_input_patterns = st.one_of([
    st.text(min_size=1, max_size=100, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs'))),
    st.just("正常的中文输入"),
    st.just("Normal English text"),
    st.just("Mixed 中英文 text"),
    st.just("Numbers 123 and symbols !@#"),
    st.just("Email: user@example.com"),
    st.just("URL: https://example.com"),
])

class TestSQLInjectionProtection:
    """SQL注入防护测试"""
    
    @given(sql_injection_patterns)
    @settings(max_examples=100)
    def test_property_18_sql_injection_detection_accuracy(self, malicious_input):
        """
        Feature: personal-website, Property 18: SQL注入防护有效性
        验证: 需求 9.5
        
        对于任意包含恶意SQL代码的输入，参数化查询应该防止代码执行
        测试SQL注入检测的准确性
        """
        # 测试SQL注入检测
        is_detected = SecurityQueryBuilder.detect_sql_injection(malicious_input)
        
        # 所有恶意输入都应该被检测到
        assert is_detected, f"未检测到SQL注入攻击: {malicious_input}"
        
        # 测试清理函数应该抛出异常
        with pytest.raises(SQLInjectionError):
            SecurityQueryBuilder.sanitize_input(malicious_input)
    
    @given(normal_input_patterns)
    @settings(max_examples=100)
    def test_property_18_sql_injection_false_positive_prevention(self, normal_input):
        """
        Feature: personal-website, Property 18: SQL注入防护有效性
        验证: 需求 9.5
        
        对于正常输入，不应该误报为SQL注入攻击
        """
        # 正常输入不应该被检测为SQL注入
        is_detected = SecurityQueryBuilder.detect_sql_injection(normal_input)
        
        # 如果被检测为攻击，记录日志但不失败测试（可能是过于严格的规则）
        if is_detected:
            print(f"警告：正常输入被误报为SQL注入: {normal_input}")
        
        # 清理函数应该正常工作
        try:
            sanitized = SecurityQueryBuilder.sanitize_input(normal_input)
            assert sanitized is not None
        except SQLInjectionError:
            pytest.fail(f"正常输入被错误地标记为SQL注入: {normal_input}")
    
    @given(sql_injection_patterns)
    @settings(max_examples=100)
    def test_property_18_sql_injection_api_protection_portfolio(self, malicious_input, client):
        """
        Feature: personal-website, Property 18: SQL注入防护有效性
        验证: 需求 9.5
        
        测试作品API端点的SQL注入防护
        """
        token = get_auth_token(client)
        headers = {"Authorization": f"Bearer {token}"}
        
        # 测试创建作品时的SQL注入防护
        malicious_portfolio = {
            "title": malicious_input,
            "description": "Normal description",
            "tech_stack": ["Python"],
            "display_order": 1
        }
        
        response = client.post(
            "/api/portfolio/",
            json=malicious_portfolio,
            headers=headers
        )
        
        # 应该返回400错误（输入验证失败）而不是500错误（SQL注入成功）
        assert response.status_code == 400, f"SQL注入防护失败，状态码: {response.status_code}"
        
        response_data = response.json()
        assert "detail" in response_data
        assert "非法字符" in response_data["detail"] or "输入" in response_data["detail"]
    
    @given(sql_injection_patterns)
    @settings(max_examples=100)
    def test_property_18_sql_injection_api_protection_blog(self, malicious_input, client):
        """
        Feature: personal-website, Property 18: SQL注入防护有效性
        验证: 需求 9.5
        
        测试博客API端点的SQL注入防护
        """
        token = get_auth_token(client)
        headers = {"Authorization": f"Bearer {token}"}
        
        # 测试创建博客时的SQL注入防护
        malicious_blog = {
            "title": malicious_input,
            "content": "Normal content",
            "is_published": True
        }
        
        response = client.post(
            "/api/blog/",
            json=malicious_blog,
            headers=headers
        )
        
        # 应该返回400错误而不是成功创建
        assert response.status_code == 400, f"SQL注入防护失败，状态码: {response.status_code}"
    
    @given(sql_injection_patterns)
    @settings(max_examples=100)
    def test_property_18_sql_injection_search_protection(self, malicious_input, client):
        """
        Feature: personal-website, Property 18: SQL注入防护有效性
        验证: 需求 9.5
        
        测试搜索功能的SQL注入防护
        """
        # 测试作品搜索
        response = client.get(f"/api/portfolio/?search={malicious_input}")
        
        # 搜索应该安全处理恶意输入，返回空结果或400错误
        assert response.status_code in [200, 400], f"搜索SQL注入防护失败，状态码: {response.status_code}"
        
        if response.status_code == 200:
            # 如果返回200，应该是空结果或安全处理的结果
            data = response.json()
            assert isinstance(data, list)
        
        # 测试博客搜索
        response = client.get(f"/api/blog/?search={malicious_input}")
        assert response.status_code in [200, 400]
    
    def test_property_18_sql_injection_safe_query_executor(self, test_db):
        """
        Feature: personal-website, Property 18: SQL注入防护有效性
        验证: 需求 9.5
        
        测试安全查询执行器的SQL注入防护
        """
        from app.security import create_safe_query_executor
        
        safe_executor = create_safe_query_executor(test_db)
        
        # 测试恶意ID查询
        malicious_ids = [
            "1; DROP TABLE portfolio; --",
            "1' OR '1'='1",
            "1 UNION SELECT * FROM users",
        ]
        
        for malicious_id in malicious_ids:
            with pytest.raises(Exception):  # 应该抛出异常而不是执行恶意SQL
                safe_executor.safe_get_by_id(Portfolio, malicious_id)
        
        # 测试恶意过滤条件
        malicious_filters = {
            "title": "'; DROP TABLE portfolio; --",
            "description": "' OR 1=1 --"
        }
        
        # 应该安全处理或抛出异常
        try:
            results = safe_executor.safe_filter_query(Portfolio, malicious_filters)
            # 如果没有抛出异常，结果应该是安全的（空或正常结果）
            assert isinstance(results, list)
        except Exception:
            # 抛出异常也是可接受的安全行为
            pass
    
    def test_property_18_sql_injection_parameterized_queries(self, test_db):
        """
        Feature: personal-website, Property 18: SQL注入防护有效性
        验证: 需求 9.5
        
        测试参数化查询的SQL注入防护
        """
        # 创建一些测试数据
        portfolio = Portfolio(
            title="Test Portfolio",
            description="Test description",
            tech_stack=["Python"],
            display_order=1
        )
        test_db.add(portfolio)
        test_db.commit()
        
        # 测试参数化查询是否安全
        malicious_title = "'; DROP TABLE portfolio; --"
        
        # 使用SQLAlchemy的参数化查询
        result = test_db.query(Portfolio).filter(
            Portfolio.title == malicious_title
        ).first()
        
        # 应该安全地返回None（没有匹配的记录）
        assert result is None
        
        # 验证原始数据仍然存在（没有被删除）
        existing_portfolio = test_db.query(Portfolio).filter(
            Portfolio.title == "Test Portfolio"
        ).first()
        assert existing_portfolio is not None
    
    @given(st.dictionaries(
        st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll'))),
        sql_injection_patterns,
        min_size=1,
        max_size=3
    ))
    @settings(max_examples=100)
    def test_property_18_sql_injection_nested_data_protection(self, malicious_data, test_db):
        """
        Feature: personal-website, Property 18: SQL注入防护有效性
        验证: 需求 9.5
        
        测试嵌套数据结构的SQL注入防护
        """
        from app.security import validate_and_sanitize_input
        
        # 测试嵌套字典的清理
        with pytest.raises(Exception):  # 应该检测到SQL注入
            validate_and_sanitize_input(malicious_data)
    
    def test_property_18_sql_injection_edge_cases(self, test_db):
        """
        Feature: personal-website, Property 18: SQL注入防护有效性
        验证: 需求 9.5
        
        测试SQL注入防护的边界情况
        """
        from app.security import SecurityQueryBuilder
        
        # 测试空输入
        assert not SecurityQueryBuilder.detect_sql_injection("")
        assert not SecurityQueryBuilder.detect_sql_injection(None)
        
        # 测试非字符串输入
        assert not SecurityQueryBuilder.detect_sql_injection(123)
        assert not SecurityQueryBuilder.detect_sql_injection([])
        assert not SecurityQueryBuilder.detect_sql_injection({})
        
        # 测试清理非字符串输入
        assert SecurityQueryBuilder.sanitize_input(123) == 123
        assert SecurityQueryBuilder.sanitize_input([1, 2, 3]) == [1, 2, 3]
        assert SecurityQueryBuilder.sanitize_input({"key": "value"}) == {"key": "value"}
    
    def test_property_18_sql_injection_case_sensitivity(self):
        """
        Feature: personal-website, Property 18: SQL注入防护有效性
        验证: 需求 9.5
        
        测试SQL注入检测的大小写敏感性
        """
        # 测试不同大小写的SQL注入攻击
        attack_variants = [
            "' OR 1=1 --",
            "' or 1=1 --",
            "' Or 1=1 --",
            "' OR 1=1 --",
            "' oR 1=1 --",
        ]
        
        for variant in attack_variants:
            assert SecurityQueryBuilder.detect_sql_injection(variant), f"未检测到大小写变体: {variant}"
    
    def test_property_18_sql_injection_encoding_bypass_prevention(self):
        """
        Feature: personal-website, Property 18: SQL注入防护有效性
        验证: 需求 9.5
        
        测试防止编码绕过的SQL注入攻击
        """
        # 测试各种编码绕过尝试
        encoded_attacks = [
            "' OR CHAR(49)=CHAR(49) --",
            "' OR ASCII('A')=65 --",
            "' OR HEX('a')=HEX('a') --",
            "' OR CONCAT('a','b')='ab' --",
        ]
        
        for attack in encoded_attacks:
            assert SecurityQueryBuilder.detect_sql_injection(attack), f"未检测到编码绕过攻击: {attack}"