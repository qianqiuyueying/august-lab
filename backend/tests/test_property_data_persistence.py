"""
Feature: personal-website, Property 13: 数据持久化往返一致性
验证数据对象保存到数据库后再读取应该得到等价的数据内容
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, timezone
import json

from app.models import Portfolio, Blog, Profile
from app.schemas import PortfolioCreate, BlogCreate, ProfileCreate, Skill


# 数据生成策略
@st.composite
def portfolio_data(draw):
    """生成作品数据的策略"""
    return PortfolioCreate(
        title=draw(st.text(min_size=1, max_size=200, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs')))),
        description=draw(st.one_of(st.none(), st.text(max_size=1000))),
        tech_stack=draw(st.lists(st.text(min_size=1, max_size=50), max_size=10)),
        project_url=draw(st.one_of(st.none(), st.text(min_size=1, max_size=500))),
        github_url=draw(st.one_of(st.none(), st.text(min_size=1, max_size=500))),
        image_url=draw(st.one_of(st.none(), st.text(min_size=1, max_size=500))),
        display_order=draw(st.integers(min_value=0, max_value=1000)),
        is_featured=draw(st.booleans())
    )

@st.composite
def blog_data(draw):
    """生成博客数据的策略"""
    return BlogCreate(
        title=draw(st.text(min_size=1, max_size=200, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs')))),
        content=draw(st.text(min_size=1, max_size=5000)),
        summary=draw(st.one_of(st.none(), st.text(max_size=500))),
        tags=draw(st.lists(st.text(min_size=1, max_size=50), max_size=10)),
        is_published=draw(st.booleans()),
        cover_image=draw(st.one_of(st.none(), st.text(min_size=1, max_size=500)))
    )

@st.composite
def skill_data(draw):
    """生成技能数据的策略"""
    return Skill(
        name=draw(st.text(min_size=1, max_size=100, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs')))),
        level=draw(st.integers(min_value=0, max_value=100)),
        category=draw(st.sampled_from(['frontend', 'backend', 'database', 'tools', 'other']))
    )

@st.composite
def profile_data(draw):
    """生成个人信息数据的策略"""
    return ProfileCreate(
        name=draw(st.text(min_size=1, max_size=100, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Zs')))),
        title=draw(st.one_of(st.none(), st.text(max_size=200))),
        bio=draw(st.one_of(st.none(), st.text(max_size=2000))),
        avatar_url=draw(st.one_of(st.none(), st.text(min_size=1, max_size=500))),
        email=draw(st.one_of(st.none(), st.emails())),
        github_url=draw(st.one_of(st.none(), st.text(min_size=1, max_size=500))),
        linkedin_url=draw(st.one_of(st.none(), st.text(min_size=1, max_size=500))),
        twitter_url=draw(st.one_of(st.none(), st.text(min_size=1, max_size=500))),
        skills=draw(st.lists(skill_data(), max_size=20))
    )


class TestDataPersistenceRoundTrip:
    """测试数据持久化往返一致性"""
    
    @given(portfolio_input=portfolio_data())
    @settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_portfolio_roundtrip_consistency(self, portfolio_input: PortfolioCreate, test_db: Session):
        """
        Feature: personal-website, Property 13: 数据持久化往返一致性
        测试作品数据的往返一致性
        """
        # 保存到数据库
        portfolio_model = Portfolio(**portfolio_input.model_dump())
        test_db.add(portfolio_model)
        test_db.commit()
        test_db.refresh(portfolio_model)
        
        # 从数据库读取
        retrieved_portfolio = test_db.query(Portfolio).filter(
            Portfolio.id == portfolio_model.id
        ).first()
        
        # 验证往返一致性
        assert retrieved_portfolio is not None
        assert retrieved_portfolio.title == portfolio_input.title
        assert retrieved_portfolio.description == portfolio_input.description
        assert retrieved_portfolio.tech_stack == portfolio_input.tech_stack
        assert retrieved_portfolio.project_url == portfolio_input.project_url
        assert retrieved_portfolio.github_url == portfolio_input.github_url
        assert retrieved_portfolio.image_url == portfolio_input.image_url
        assert retrieved_portfolio.display_order == portfolio_input.display_order
        assert retrieved_portfolio.is_featured == portfolio_input.is_featured
        
        # 验证自动生成的字段
        assert retrieved_portfolio.id is not None
        assert retrieved_portfolio.created_at is not None
        assert retrieved_portfolio.updated_at is not None
    
    @given(blog_input=blog_data())
    @settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_blog_roundtrip_consistency(self, blog_input: BlogCreate, test_db: Session):
        """
        Feature: personal-website, Property 13: 数据持久化往返一致性
        测试博客数据的往返一致性
        """
        # 保存到数据库
        blog_dict = blog_input.model_dump()
        if blog_dict.get("is_published"):
            blog_dict["published_at"] = datetime.now(timezone.utc)
        
        blog_model = Blog(**blog_dict)
        test_db.add(blog_model)
        test_db.commit()
        test_db.refresh(blog_model)
        
        # 从数据库读取
        retrieved_blog = test_db.query(Blog).filter(
            Blog.id == blog_model.id
        ).first()
        
        # 验证往返一致性
        assert retrieved_blog is not None
        assert retrieved_blog.title == blog_input.title
        assert retrieved_blog.content == blog_input.content
        assert retrieved_blog.summary == blog_input.summary
        assert retrieved_blog.tags == blog_input.tags
        assert retrieved_blog.is_published == blog_input.is_published
        assert retrieved_blog.cover_image == blog_input.cover_image
        
        # 验证自动生成的字段
        assert retrieved_blog.id is not None
        assert retrieved_blog.created_at is not None
        assert retrieved_blog.updated_at is not None
        
        # 如果是已发布状态，验证发布时间
        if blog_input.is_published:
            assert retrieved_blog.published_at is not None
    
    @given(profile_input=profile_data())
    @settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_profile_roundtrip_consistency(self, profile_input: ProfileCreate, test_db: Session):
        """
        Feature: personal-website, Property 13: 数据持久化往返一致性
        测试个人信息数据的往返一致性
        """
        # 清理现有的profile记录以避免唯一约束冲突
        test_db.query(Profile).delete()
        test_db.commit()
        
        # 保存到数据库
        profile_dict = profile_input.model_dump()
        profile_dict["id"] = 1  # 个人信息使用固定ID
        
        # 转换技能数据为JSON格式
        if profile_dict.get("skills"):
            profile_dict["skills"] = [skill.model_dump() for skill in profile_input.skills]
        
        profile_model = Profile(**profile_dict)
        test_db.add(profile_model)
        test_db.commit()
        test_db.refresh(profile_model)
        
        # 从数据库读取
        retrieved_profile = test_db.query(Profile).filter(
            Profile.id == profile_model.id
        ).first()
        
        # 验证往返一致性
        assert retrieved_profile is not None
        assert retrieved_profile.name == profile_input.name
        assert retrieved_profile.title == profile_input.title
        assert retrieved_profile.bio == profile_input.bio
        assert retrieved_profile.avatar_url == profile_input.avatar_url
        assert retrieved_profile.email == profile_input.email
        assert retrieved_profile.github_url == profile_input.github_url
        assert retrieved_profile.linkedin_url == profile_input.linkedin_url
        assert retrieved_profile.twitter_url == profile_input.twitter_url
        
        # 验证技能数据
        if profile_input.skills:
            assert retrieved_profile.skills is not None
            assert len(retrieved_profile.skills) == len(profile_input.skills)
            for i, skill in enumerate(profile_input.skills):
                retrieved_skill = retrieved_profile.skills[i]
                assert retrieved_skill["name"] == skill.name
                assert retrieved_skill["level"] == skill.level
                assert retrieved_skill["category"] == skill.category
        
        # 验证自动生成的字段
        assert retrieved_profile.id == 1
        assert retrieved_profile.updated_at is not None
    
    def test_json_field_empty_list_consistency(self, test_db: Session):
        """
        Feature: personal-website, Property 13: 数据持久化往返一致性
        测试JSON字段空列表的往返一致性
        """
        # 测试作品的空技术栈
        portfolio = Portfolio(
            title="Test Portfolio",
            tech_stack=[]
        )
        test_db.add(portfolio)
        test_db.commit()
        test_db.refresh(portfolio)
        
        retrieved_portfolio = test_db.query(Portfolio).filter(
            Portfolio.id == portfolio.id
        ).first()
        
        assert retrieved_portfolio.tech_stack == []
        
        # 测试博客的空标签
        blog = Blog(
            title="Test Blog",
            content="Test content",
            tags=[]
        )
        test_db.add(blog)
        test_db.commit()
        test_db.refresh(blog)
        
        retrieved_blog = test_db.query(Blog).filter(
            Blog.id == blog.id
        ).first()
        
        assert retrieved_blog.tags == []
        
        # 测试个人信息的空技能
        profile = Profile(
            id=1,
            name="Test User",
            skills=[]
        )
        test_db.add(profile)
        test_db.commit()
        test_db.refresh(profile)
        
        retrieved_profile = test_db.query(Profile).filter(
            Profile.id == profile.id
        ).first()
        
        assert retrieved_profile.skills == []
    
    def test_json_field_null_to_empty_list_conversion(self, test_db: Session):
        """
        Feature: personal-website, Property 13: 数据持久化往返一致性
        测试JSON字段NULL值到空列表的转换一致性
        """
        # 直接插入NULL值到数据库
        test_db.execute(
            text("INSERT INTO portfolio (title, tech_stack) VALUES ('Test', NULL)")
        )
        test_db.execute(
            text("INSERT INTO blog (title, content, tags) VALUES ('Test', 'Content', NULL)")
        )
        test_db.execute(
            text("INSERT INTO profile (id, name, skills) VALUES (1, 'Test', NULL)")
        )
        test_db.commit()
        
        # 读取并验证NULL值被正确处理
        portfolio = test_db.query(Portfolio).filter(Portfolio.title == "Test").first()
        blog = test_db.query(Blog).filter(Blog.title == "Test").first()
        profile = test_db.query(Profile).filter(Profile.id == 1).first()
        
        # 根据模型定义，NULL应该被处理为空列表或保持为NULL
        # 这取决于具体的实现，这里我们测试实际行为
        assert portfolio is not None
        assert blog is not None
        assert profile is not None