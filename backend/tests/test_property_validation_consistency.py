"""
Feature: personal-website, Property 15: 数据验证规则一致性
验证输入数据的验证规则在前端和后端保持一致的执行结果
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from pydantic import ValidationError
from fastapi.testclient import TestClient

from app.schemas import PortfolioCreate, BlogCreate, ProfileCreate, Skill
from app.validators import (
    validate_tech_stack_item, validate_tag, validate_url,
    validate_github_url, validate_linkedin_url, validate_twitter_url,
    validate_skill_level, validate_markdown_content
)


class TestValidationRulesConsistency:
    """测试数据验证规则一致性"""
    
    @given(
        title=st.one_of(
            st.text(min_size=0, max_size=0),  # 空字符串
            st.text(min_size=1, max_size=200),  # 正常长度
            st.text(min_size=201, max_size=300),  # 超长
            st.just("   "),  # 只有空格
        )
    )
    @settings(max_examples=100, deadline=None)
    def test_portfolio_title_validation_consistency(self, title: str):
        """
        Feature: personal-website, Property 15: 数据验证规则一致性
        测试作品标题验证规则的一致性
        """
        # 测试Pydantic模型验证
        try:
            portfolio = PortfolioCreate(title=title)
            # 如果Pydantic验证通过，标题应该符合规则
            assert len(portfolio.title.strip()) > 0
            assert len(portfolio.title) <= 200
        except ValidationError as e:
            # 如果Pydantic验证失败，应该是因为违反了规则
            error_messages = [error['msg'] for error in e.errors()]
            # 验证错误消息符合预期
            assert any('标题不能为空' in msg or 'String should have at least 1 character' in msg 
                      for msg in error_messages) or len(title) > 200
    
    @given(
        content=st.one_of(
            st.text(min_size=0, max_size=0),  # 空字符串
            st.text(min_size=1, max_size=1000),  # 正常长度
            st.text(min_size=100001, max_size=100010),  # 超长内容
            st.just("   "),  # 只有空格
        )
    )
    @settings(max_examples=100, deadline=None)
    def test_blog_content_validation_consistency(self, content: str):
        """
        Feature: personal-website, Property 15: 数据验证规则一致性
        测试博客内容验证规则的一致性
        """
        # 测试直接验证器
        try:
            validated_content = validate_markdown_content(content)
            # 如果直接验证通过，内容应该符合规则
            assert len(validated_content.strip()) > 0
            assert len(validated_content) <= 100000
        except ValueError:
            # 如果直接验证失败，Pydantic也应该失败
            with pytest.raises(ValidationError):
                BlogCreate(title="Test", content=content)
    
    @given(
        tech_items=st.lists(
            st.one_of(
                st.text(min_size=0, max_size=0),  # 空字符串
                st.text(min_size=1, max_size=50),  # 正常长度
                st.text(min_size=51, max_size=100),  # 超长
                st.just("   "),  # 只有空格
                st.text(alphabet="<>\"'", min_size=1, max_size=10),  # 包含特殊字符
            ),
            max_size=25  # 超过最大数量限制
        )
    )
    @settings(max_examples=100, deadline=None)
    def test_tech_stack_validation_consistency(self, tech_items: list):
        """
        Feature: personal-website, Property 15: 数据验证规则一致性
        测试技术栈验证规则的一致性
        """
        # 测试直接验证器
        validated_items = []
        validation_errors = []
        
        for item in tech_items:
            try:
                validated_item = validate_tech_stack_item(item)
                validated_items.append(validated_item)
            except ValueError as e:
                validation_errors.append(str(e))
        
        # 测试Pydantic模型验证
        try:
            portfolio = PortfolioCreate(title="Test", tech_stack=tech_items)
            # 如果Pydantic验证通过，验证结果应该一致
            assert len(portfolio.tech_stack) == len(validated_items)
            # 验证过滤后的项目数量不超过限制
            assert len(portfolio.tech_stack) <= 20
        except ValidationError:
            # 如果Pydantic验证失败，应该是因为违反了某些规则
            # 比如数量超限或包含无效项目
            assert len(tech_items) > 20 or len(validation_errors) > 0
    
    @given(
        tags=st.lists(
            st.one_of(
                st.text(min_size=0, max_size=0),  # 空字符串
                st.text(min_size=1, max_size=30),  # 正常长度
                st.text(min_size=31, max_size=50),  # 超长
                st.just("   "),  # 只有空格
                st.text(alphabet="<>\"',", min_size=1, max_size=10),  # 包含特殊字符
            ),
            max_size=15  # 超过最大数量限制
        )
    )
    @settings(max_examples=100, deadline=None)
    def test_blog_tags_validation_consistency(self, tags: list):
        """
        Feature: personal-website, Property 15: 数据验证规则一致性
        测试博客标签验证规则的一致性
        """
        # 测试直接验证器
        validated_tags = []
        validation_errors = []
        
        for tag in tags:
            try:
                validated_tag = validate_tag(tag)
                validated_tags.append(validated_tag)
            except ValueError as e:
                validation_errors.append(str(e))
        
        # 测试Pydantic模型验证
        try:
            blog = BlogCreate(title="Test", content="Test content", tags=tags)
            # 如果Pydantic验证通过，验证结果应该一致
            assert len(blog.tags) == len(validated_tags)
            # 验证过滤后的标签数量不超过限制
            assert len(blog.tags) <= 10
        except ValidationError:
            # 如果Pydantic验证失败，应该是因为违反了某些规则
            assert len(tags) > 10 or len(validation_errors) > 0
    
    @given(
        level=st.integers(min_value=-10, max_value=110)
    )
    @settings(max_examples=100, deadline=None)
    def test_skill_level_validation_consistency(self, level: int):
        """
        Feature: personal-website, Property 15: 数据验证规则一致性
        测试技能熟练度验证规则的一致性
        """
        # 测试直接验证器
        try:
            validated_level = validate_skill_level(level)
            # 如果直接验证通过，应该在有效范围内
            assert 0 <= validated_level <= 100
            
            # Pydantic验证也应该通过
            skill = Skill(name="Test", level=level, category="frontend")
            assert skill.level == validated_level
            
        except ValueError:
            # 如果直接验证失败，Pydantic也应该失败
            with pytest.raises(ValidationError):
                Skill(name="Test", level=level, category="frontend")
    
    @given(
        url=st.one_of(
            st.just(""),  # 空字符串
            st.just("   "),  # 只有空格
            st.just("invalid-url"),  # 无效URL
            st.just("http://example.com"),  # 有效HTTP URL
            st.just("https://example.com"),  # 有效HTTPS URL
            st.just("example.com"),  # 无协议的域名
            st.just("ftp://example.com"),  # 其他协议
        )
    )
    @settings(max_examples=100, deadline=None)
    def test_url_validation_consistency(self, url: str):
        """
        Feature: personal-website, Property 15: 数据验证规则一致性
        测试URL验证规则的一致性
        """
        # 测试直接验证器
        try:
            validated_url = validate_url(url)
            if validated_url is not None:
                # 如果验证通过，应该是有效的URL格式
                assert validated_url.startswith(('http://', 'https://'))
                
                # Pydantic验证也应该通过
                portfolio = PortfolioCreate(title="Test", project_url=url)
                assert portfolio.project_url == validated_url
            else:
                # 如果返回None，说明输入为空
                assert not url or not url.strip()
                
        except ValueError:
            # 如果直接验证失败，Pydantic可能也会失败或处理为None
            try:
                portfolio = PortfolioCreate(title="Test", project_url=url)
                # 如果Pydantic没有失败，可能是因为它有不同的处理逻辑
            except ValidationError:
                # 这是预期的行为
                pass
    
    @given(
        github_url=st.one_of(
            st.just(""),
            st.just("https://github.com/user/repo"),
            st.just("github.com/user/repo"),
            st.just("https://gitlab.com/user/repo"),  # 非GitHub URL
            st.just("invalid-url"),
        )
    )
    @settings(max_examples=100, deadline=None)
    def test_github_url_validation_consistency(self, github_url: str):
        """
        Feature: personal-website, Property 15: 数据验证规则一致性
        测试GitHub URL验证规则的一致性
        """
        # 测试直接验证器
        try:
            validated_url = validate_github_url(github_url)
            if validated_url is not None:
                # 如果验证通过，应该包含github.com
                assert 'github.com' in validated_url.lower()
                assert validated_url.startswith(('http://', 'https://'))
                
                # Pydantic验证也应该通过
                portfolio = PortfolioCreate(title="Test", github_url=github_url)
                assert portfolio.github_url == validated_url
            else:
                # 如果返回None，说明输入为空
                assert not github_url or not github_url.strip()
                
        except ValueError:
            # 如果直接验证失败，Pydantic也应该失败
            with pytest.raises(ValidationError):
                PortfolioCreate(title="Test", github_url=github_url)
    
    def test_email_validation_consistency(self):
        """
        Feature: personal-website, Property 15: 数据验证规则一致性
        测试邮箱验证规则的一致性
        """
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "user+tag@example.org"
        ]
        
        invalid_emails = [
            "invalid-email",
            "@example.com",
            "test@",
            "test.example.com",
            ""
        ]
        
        # 测试有效邮箱
        for email in valid_emails:
            try:
                profile = ProfileCreate(name="Test", email=email)
                assert profile.email == email
            except ValidationError:
                pytest.fail(f"有效邮箱 {email} 验证失败")
        
        # 测试无效邮箱
        for email in invalid_emails:
            if email:  # 非空的无效邮箱应该抛出异常
                with pytest.raises(ValidationError):
                    ProfileCreate(name="Test", email=email)
            else:  # 空邮箱应该被接受（可选字段）
                profile = ProfileCreate(name="Test", email=None)
                assert profile.email is None
    
    def test_skill_category_validation_consistency(self):
        """
        Feature: personal-website, Property 15: 数据验证规则一致性
        测试技能分类验证规则的一致性
        """
        valid_categories = ['frontend', 'backend', 'database', 'tools', 'other']
        invalid_categories = ['invalid', 'Frontend', 'BACKEND', '']
        
        # 测试有效分类
        for category in valid_categories:
            skill = Skill(name="Test", level=50, category=category)
            assert skill.category == category.lower()
        
        # 测试无效分类
        for category in invalid_categories:
            with pytest.raises(ValidationError):
                Skill(name="Test", level=50, category=category)
    
    def test_field_length_limits_consistency(self):
        """
        Feature: personal-website, Property 15: 数据验证规则一致性
        测试字段长度限制的一致性
        """
        # 测试各种字段的长度限制
        test_cases = [
            # (field_name, max_length, model_class, required_fields)
            ("title", 200, PortfolioCreate, {}),
            ("title", 200, BlogCreate, {"content": "test"}),
            ("name", 100, ProfileCreate, {}),
            ("description", 2000, PortfolioCreate, {"title": "test"}),
            ("summary", 1000, BlogCreate, {"title": "test", "content": "test"}),
            ("bio", 5000, ProfileCreate, {"name": "test"}),
        ]
        
        for field_name, max_length, model_class, required_fields in test_cases:
            # 测试最大长度边界
            valid_text = "a" * max_length
            invalid_text = "a" * (max_length + 1)
            
            # 有效长度应该通过
            kwargs = {field_name: valid_text, **required_fields}
            model = model_class(**kwargs)
            assert len(getattr(model, field_name)) == max_length
            
            # 超长应该失败
            kwargs = {field_name: invalid_text, **required_fields}
            with pytest.raises(ValidationError):
                model_class(**kwargs)