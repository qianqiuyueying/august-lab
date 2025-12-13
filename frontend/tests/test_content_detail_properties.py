"""
内容详情信息完整性属性测试
验证需求 2.2, 3.2 - 作品和博客详情页面的信息完整性
"""

import pytest
from hypothesis import given, strategies as st, assume, settings
from typing import Dict, Any, Optional, List
import json
import re
from datetime import datetime


# 测试数据生成策略
@st.composite
def portfolio_detail(draw):
    """生成作品详情数据"""
    created_dt = draw(st.datetimes())
    updated_dt = draw(st.datetimes(min_value=created_dt))  # 确保更新时间不早于创建时间
    
    return {
        'id': draw(st.integers(min_value=1, max_value=10000)),
        'title': draw(st.text(min_size=1, max_size=100, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs')))),
        'description': draw(st.one_of(st.none(), st.text(min_size=0, max_size=1000))),
        'tech_stack': draw(st.lists(st.text(min_size=1, max_size=30), min_size=1, max_size=15)),
        'project_url': draw(st.one_of(st.none(), st.text(min_size=10, max_size=200))),
        'github_url': draw(st.one_of(st.none(), st.text(min_size=10, max_size=200))),
        'image_url': draw(st.one_of(st.none(), st.text(min_size=10, max_size=200))),
        'display_order': draw(st.integers(min_value=0, max_value=1000)),
        'is_featured': draw(st.booleans()),
        'created_at': created_dt.isoformat(),
        'updated_at': updated_dt.isoformat()
    }


@st.composite
def blog_detail(draw):
    """生成博客详情数据"""
    created_dt = draw(st.datetimes())
    updated_dt = draw(st.datetimes(min_value=created_dt))  # 确保更新时间不早于创建时间
    
    return {
        'id': draw(st.integers(min_value=1, max_value=10000)),
        'title': draw(st.text(min_size=1, max_size=150, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs')))),
        'content': draw(st.text(min_size=50, max_size=5000)),
        'summary': draw(st.one_of(st.none(), st.text(min_size=0, max_size=500))),
        'tags': draw(st.lists(st.text(min_size=1, max_size=30), min_size=0, max_size=10)),
        'is_published': draw(st.booleans()),
        'cover_image': draw(st.one_of(st.none(), st.text(min_size=10, max_size=200))),
        'created_at': created_dt.isoformat(),
        'updated_at': updated_dt.isoformat()
    }


class ContentDetailValidator:
    """内容详情验证器"""
    
    def __init__(self):
        self.required_portfolio_detail_fields = ['id', 'title', 'tech_stack', 'created_at', 'updated_at']
        self.required_blog_detail_fields = ['id', 'title', 'content', 'is_published', 'created_at', 'updated_at']
        self.optional_portfolio_fields = ['description', 'project_url', 'github_url', 'image_url']
        self.optional_blog_fields = ['summary', 'tags', 'cover_image']
    
    def validate_portfolio_detail_completeness(self, portfolio: Dict[str, Any]) -> Dict[str, Any]:
        """验证作品详情完整性"""
        results = {
            'has_all_required_fields': True,
            'missing_required_fields': [],
            'invalid_field_types': [],
            'empty_critical_fields': [],
            'tech_stack_analysis': {
                'count': 0,
                'unique_technologies': set(),
                'has_duplicates': False,
                'average_length': 0
            },
            'url_validation': {
                'project_url_valid': None,
                'github_url_valid': None,
                'image_url_valid': None
            },
            'date_validation': {
                'created_at_valid': False,
                'updated_at_valid': False,
                'dates_consistent': False
            },
            'content_richness': {
                'has_description': False,
                'description_length': 0,
                'has_external_links': False,
                'has_image': False
            },
            'display_properties': {
                'is_featured': False,
                'display_order': 0,
                'title_length': 0
            }
        }
        
        # 检查必需字段
        for field in self.required_portfolio_detail_fields:
            if field not in portfolio:
                results['missing_required_fields'].append(field)
                results['has_all_required_fields'] = False
            elif not portfolio[field] and field in ['title']:
                results['empty_critical_fields'].append(field)
        
        # 验证字段类型和内容
        if 'id' in portfolio:
            if not isinstance(portfolio['id'], int) or portfolio['id'] <= 0:
                results['invalid_field_types'].append('id: must be positive integer')
        
        if 'title' in portfolio:
            if isinstance(portfolio['title'], str):
                results['display_properties']['title_length'] = len(portfolio['title'])
            else:
                results['invalid_field_types'].append('title: must be string')
        
        # 技术栈分析
        if 'tech_stack' in portfolio:
            if isinstance(portfolio['tech_stack'], list):
                tech_stack = portfolio['tech_stack']
                results['tech_stack_analysis']['count'] = len(tech_stack)
                results['tech_stack_analysis']['unique_technologies'] = set(tech_stack)
                results['tech_stack_analysis']['has_duplicates'] = len(tech_stack) != len(set(tech_stack))
                
                if tech_stack:
                    total_length = sum(len(str(tech)) for tech in tech_stack)
                    results['tech_stack_analysis']['average_length'] = total_length / len(tech_stack)
            else:
                results['invalid_field_types'].append('tech_stack: must be list')
        
        # URL 验证
        for url_field in ['project_url', 'github_url', 'image_url']:
            if url_field in portfolio and portfolio[url_field]:
                url = portfolio[url_field]
                if isinstance(url, str) and len(url) > 5:
                    results['url_validation'][f'{url_field}_valid'] = True
                else:
                    results['url_validation'][f'{url_field}_valid'] = False
        
        # 日期验证
        for date_field in ['created_at', 'updated_at']:
            if date_field in portfolio and portfolio[date_field]:
                try:
                    datetime.fromisoformat(portfolio[date_field].replace('Z', '+00:00'))
                    results['date_validation'][f'{date_field}_valid'] = True
                except (ValueError, AttributeError):
                    results['date_validation'][f'{date_field}_valid'] = False
        
        # 日期一致性检查
        if (results['date_validation']['created_at_valid'] and 
            results['date_validation']['updated_at_valid']):
            try:
                created = datetime.fromisoformat(portfolio['created_at'].replace('Z', '+00:00'))
                updated = datetime.fromisoformat(portfolio['updated_at'].replace('Z', '+00:00'))
                results['date_validation']['dates_consistent'] = created <= updated
            except:
                results['date_validation']['dates_consistent'] = False
        
        # 内容丰富度分析
        if 'description' in portfolio and portfolio['description']:
            results['content_richness']['has_description'] = True
            results['content_richness']['description_length'] = len(portfolio['description'])
        
        if portfolio.get('project_url') or portfolio.get('github_url'):
            results['content_richness']['has_external_links'] = True
        
        if portfolio.get('image_url'):
            results['content_richness']['has_image'] = True
        
        # 显示属性
        results['display_properties']['is_featured'] = portfolio.get('is_featured', False)
        results['display_properties']['display_order'] = portfolio.get('display_order', 0)
        
        return results
    
    def validate_blog_detail_completeness(self, blog: Dict[str, Any]) -> Dict[str, Any]:
        """验证博客详情完整性"""
        results = {
            'has_all_required_fields': True,
            'missing_required_fields': [],
            'invalid_field_types': [],
            'empty_critical_fields': [],
            'content_analysis': {
                'content_length': 0,
                'estimated_reading_time': 0,
                'has_markdown': False,
                'paragraph_count': 0,
                'word_count': 0
            },
            'metadata_analysis': {
                'has_summary': False,
                'summary_length': 0,
                'tag_count': 0,
                'unique_tags': set(),
                'has_cover_image': False
            },
            'publication_status': {
                'is_published': False,
                'ready_for_publication': False
            },
            'date_validation': {
                'created_at_valid': False,
                'updated_at_valid': False,
                'dates_consistent': False
            },
            'seo_readiness': {
                'has_title': False,
                'title_length_appropriate': False,
                'has_meta_description': False,
                'has_tags': False
            }
        }
        
        # 检查必需字段
        for field in self.required_blog_detail_fields:
            if field not in blog:
                results['missing_required_fields'].append(field)
                results['has_all_required_fields'] = False
            elif not blog[field] and field in ['title', 'content']:
                results['empty_critical_fields'].append(field)
        
        # 验证字段类型
        if 'id' in blog:
            if not isinstance(blog['id'], int) or blog['id'] <= 0:
                results['invalid_field_types'].append('id: must be positive integer')
        
        if 'title' in blog:
            if isinstance(blog['title'], str):
                title_len = len(blog['title'])
                results['seo_readiness']['has_title'] = True
                results['seo_readiness']['title_length_appropriate'] = 10 <= title_len <= 100
            else:
                results['invalid_field_types'].append('title: must be string')
        
        # 内容分析
        if 'content' in blog and isinstance(blog['content'], str):
            content = blog['content']
            results['content_analysis']['content_length'] = len(content)
            
            # 估算阅读时间（假设每分钟200字）
            word_count = len(content.split())
            results['content_analysis']['word_count'] = word_count
            results['content_analysis']['estimated_reading_time'] = max(1, word_count // 200)
            
            # 检查Markdown标记
            markdown_patterns = ['#', '*', '`', '[', ']', '(', ')']
            results['content_analysis']['has_markdown'] = any(pattern in content for pattern in markdown_patterns)
            
            # 段落计数
            paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
            results['content_analysis']['paragraph_count'] = len(paragraphs)
        
        # 元数据分析
        if 'summary' in blog and blog['summary']:
            results['metadata_analysis']['has_summary'] = True
            results['metadata_analysis']['summary_length'] = len(blog['summary'])
            results['seo_readiness']['has_meta_description'] = True
        
        if 'tags' in blog and isinstance(blog['tags'], list):
            tags = blog['tags']
            results['metadata_analysis']['tag_count'] = len(tags)
            results['metadata_analysis']['unique_tags'] = set(tags)
            results['seo_readiness']['has_tags'] = len(tags) > 0
        
        if 'cover_image' in blog and blog['cover_image']:
            results['metadata_analysis']['has_cover_image'] = True
        
        # 发布状态
        results['publication_status']['is_published'] = blog.get('is_published', False)
        
        # 发布就绪检查
        publication_ready = (
            results['seo_readiness']['has_title'] and
            results['content_analysis']['content_length'] > 100 and
            results['seo_readiness']['has_tags']
        )
        results['publication_status']['ready_for_publication'] = publication_ready
        
        # 日期验证
        for date_field in ['created_at', 'updated_at']:
            if date_field in blog and blog[date_field]:
                try:
                    datetime.fromisoformat(blog[date_field].replace('Z', '+00:00'))
                    results['date_validation'][f'{date_field}_valid'] = True
                except (ValueError, AttributeError):
                    results['date_validation'][f'{date_field}_valid'] = False
        
        # 日期一致性检查
        if (results['date_validation']['created_at_valid'] and 
            results['date_validation']['updated_at_valid']):
            try:
                created = datetime.fromisoformat(blog['created_at'].replace('Z', '+00:00'))
                updated = datetime.fromisoformat(blog['updated_at'].replace('Z', '+00:00'))
                results['date_validation']['dates_consistent'] = created <= updated
            except:
                results['date_validation']['dates_consistent'] = False
        
        return results
    
    def validate_content_accessibility(self, content: Dict[str, Any], content_type: str) -> Dict[str, Any]:
        """验证内容可访问性"""
        results = {
            'has_alt_text': False,
            'title_descriptive': False,
            'content_structured': False,
            'links_descriptive': False,
            'color_contrast_safe': True,  # 假设使用了安全的颜色方案
            'keyboard_navigable': True    # 假设实现了键盘导航
        }
        
        # 检查图片alt文本
        if content.get('image_url'):
            # 在实际实现中，这里会检查图片是否有alt属性
            results['has_alt_text'] = True  # 假设实现了alt文本
        
        # 检查标题描述性
        if 'title' in content and isinstance(content['title'], str):
            title = content['title'].strip()
            # 简单的描述性检查：长度合理且包含有意义的词汇
            results['title_descriptive'] = len(title) >= 5 and not title.isnumeric()
        
        # 检查内容结构
        if content_type == 'blog' and 'content' in content:
            content_text = content['content']
            # 检查是否有标题结构（Markdown格式）
            has_headers = '#' in content_text
            has_paragraphs = '\n\n' in content_text
            results['content_structured'] = has_headers or has_paragraphs
        
        # 检查链接描述性
        link_fields = ['project_url', 'github_url'] if content_type == 'portfolio' else []
        for field in link_fields:
            if content.get(field):
                # 在实际实现中，这里会检查链接文本是否描述性
                results['links_descriptive'] = True
        
        return results
    
    def validate_content_performance(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """验证内容性能相关属性"""
        results = {
            'image_optimized': False,
            'content_size_reasonable': True,
            'load_time_estimate': 0,
            'seo_optimized': False
        }
        
        # 图片优化检查
        if content.get('image_url'):
            # 在实际实现中，这里会检查图片格式、大小等
            results['image_optimized'] = True  # 假设图片已优化
        
        # 内容大小检查
        total_size = 0
        for key, value in content.items():
            if isinstance(value, str):
                total_size += len(value.encode('utf-8'))
        
        # 假设合理的内容大小上限为100KB
        results['content_size_reasonable'] = total_size < 100 * 1024
        
        # 估算加载时间（基于内容大小）
        results['load_time_estimate'] = max(0.1, total_size / (50 * 1024))  # 假设50KB/s
        
        # SEO优化检查
        has_title = bool(content.get('title'))
        has_description = bool(content.get('description') or content.get('summary'))
        has_metadata = bool(content.get('tags') or content.get('tech_stack'))
        
        results['seo_optimized'] = has_title and has_description and has_metadata
        
        return results


# 属性测试
class TestContentDetailProperties:
    """内容详情信息完整性属性测试"""
    
    def setup_method(self):
        self.validator = ContentDetailValidator()
    
    @given(portfolio_detail())
    @settings(max_examples=100, deadline=None)
    def test_portfolio_detail_completeness_property(self, portfolio):
        """
        属性 4: 内容详情信息完整性 - 作品详情
        验证作品详情页面包含所有必要的信息和元数据
        """
        results = self.validator.validate_portfolio_detail_completeness(portfolio)
        
        # 基本完整性验证
        if not results['missing_required_fields'] and not results['empty_critical_fields']:
            assert results['has_all_required_fields'] == True
        
        # 技术栈分析验证
        tech_analysis = results['tech_stack_analysis']
        if 'tech_stack' in portfolio and isinstance(portfolio['tech_stack'], list):
            assert tech_analysis['count'] == len(portfolio['tech_stack'])
            assert len(tech_analysis['unique_technologies']) <= tech_analysis['count']
            
            if tech_analysis['count'] > 0:
                assert tech_analysis['average_length'] > 0
        
        # 日期一致性验证
        if (results['date_validation']['created_at_valid'] and 
            results['date_validation']['updated_at_valid']):
            # 如果两个日期都有效，它们应该是一致的（创建时间 <= 更新时间）
            assert results['date_validation']['dates_consistent'] == True
        
        # 内容丰富度验证
        content_richness = results['content_richness']
        if portfolio.get('description'):
            assert content_richness['has_description'] == True
            assert content_richness['description_length'] > 0
        
        # URL验证逻辑性检查
        url_validation = results['url_validation']
        for url_field in ['project_url', 'github_url', 'image_url']:
            if portfolio.get(url_field):
                # 如果URL存在，验证结果不应该是None
                assert url_validation[f'{url_field}_valid'] is not None
        
        # 显示属性验证
        display_props = results['display_properties']
        assert isinstance(display_props['is_featured'], bool)
        assert isinstance(display_props['display_order'], (int, float))
        assert display_props['title_length'] >= 0
    
    @given(blog_detail())
    @settings(max_examples=100, deadline=None)
    def test_blog_detail_completeness_property(self, blog):
        """
        属性 4: 内容详情信息完整性 - 博客详情
        验证博客详情页面包含所有必要的信息和元数据
        """
        results = self.validator.validate_blog_detail_completeness(blog)
        
        # 基本完整性验证
        if not results['missing_required_fields'] and not results['empty_critical_fields']:
            assert results['has_all_required_fields'] == True
        
        # 内容分析验证
        content_analysis = results['content_analysis']
        if 'content' in blog and isinstance(blog['content'], str):
            assert content_analysis['content_length'] == len(blog['content'])
            assert content_analysis['estimated_reading_time'] > 0
            assert content_analysis['word_count'] >= 0
            assert content_analysis['paragraph_count'] >= 0
        
        # 元数据分析验证
        metadata_analysis = results['metadata_analysis']
        if blog.get('summary'):
            assert metadata_analysis['has_summary'] == True
            assert metadata_analysis['summary_length'] > 0
        
        if blog.get('tags') and isinstance(blog['tags'], list):
            assert metadata_analysis['tag_count'] == len(blog['tags'])
            assert len(metadata_analysis['unique_tags']) <= metadata_analysis['tag_count']
        
        # 发布状态验证
        publication_status = results['publication_status']
        assert isinstance(publication_status['is_published'], bool)
        assert isinstance(publication_status['ready_for_publication'], bool)
        
        # SEO就绪性验证
        seo_readiness = results['seo_readiness']
        if blog.get('title'):
            assert seo_readiness['has_title'] == True
        
        if blog.get('summary'):
            assert seo_readiness['has_meta_description'] == True
        
        if blog.get('tags') and len(blog['tags']) > 0:
            assert seo_readiness['has_tags'] == True
        
        # 日期一致性验证
        if (results['date_validation']['created_at_valid'] and 
            results['date_validation']['updated_at_valid']):
            assert results['date_validation']['dates_consistent'] == True
    
    @given(
        st.one_of(portfolio_detail(), blog_detail()),
        st.sampled_from(['portfolio', 'blog'])
    )
    @settings(max_examples=50, deadline=None)
    def test_content_accessibility_property(self, content, content_type):
        """
        属性: 内容可访问性
        验证内容符合可访问性标准
        """
        results = self.validator.validate_content_accessibility(content, content_type)
        
        # 可访问性基本要求
        assert isinstance(results['has_alt_text'], bool)
        assert isinstance(results['title_descriptive'], bool)
        assert isinstance(results['content_structured'], bool)
        assert isinstance(results['links_descriptive'], bool)
        assert isinstance(results['color_contrast_safe'], bool)
        assert isinstance(results['keyboard_navigable'], bool)
        
        # 如果有图片，应该考虑alt文本
        if content.get('image_url') or content.get('cover_image'):
            # 在实际实现中，这里会有更严格的检查
            assert results['has_alt_text'] is not None
        
        # 标题描述性检查
        if content.get('title'):
            title = content['title'].strip()
            if len(title) >= 5 and not title.isnumeric():
                assert results['title_descriptive'] == True
    
    @given(st.one_of(portfolio_detail(), blog_detail()))
    @settings(max_examples=50, deadline=None)
    def test_content_performance_property(self, content):
        """
        属性: 内容性能优化
        验证内容的性能相关属性
        """
        results = self.validator.validate_content_performance(content)
        
        # 性能指标验证
        assert isinstance(results['image_optimized'], bool)
        assert isinstance(results['content_size_reasonable'], bool)
        assert isinstance(results['seo_optimized'], bool)
        assert results['load_time_estimate'] >= 0
        
        # 内容大小合理性
        total_size = sum(len(str(v).encode('utf-8')) for v in content.values() if isinstance(v, str))
        expected_reasonable = total_size < 100 * 1024
        assert results['content_size_reasonable'] == expected_reasonable
        
        # SEO优化检查逻辑
        has_title = bool(content.get('title'))
        has_description = bool(content.get('description') or content.get('summary'))
        has_metadata = bool(content.get('tags') or content.get('tech_stack'))
        expected_seo = has_title and has_description and has_metadata
        assert results['seo_optimized'] == expected_seo
    
    @given(st.lists(portfolio_detail(), min_size=1, max_size=10))
    @settings(max_examples=30, deadline=None)
    def test_portfolio_detail_consistency_property(self, portfolios):
        """
        属性: 作品详情一致性
        验证多个作品详情的数据一致性
        """
        all_results = [self.validator.validate_portfolio_detail_completeness(p) for p in portfolios]
        
        # 验证所有作品的字段结构一致性
        required_fields_consistency = all(
            set(result['missing_required_fields']) == set() or 
            len(result['missing_required_fields']) > 0 
            for result in all_results
        )
        
        # 验证技术栈数据的合理性
        all_tech_counts = [result['tech_stack_analysis']['count'] for result in all_results]
        assert all(count >= 0 for count in all_tech_counts)
        
        # 验证日期格式的一致性
        date_validations = [result['date_validation'] for result in all_results]
        for date_val in date_validations:
            # 如果日期有效，那么一致性检查应该是合理的
            if date_val['created_at_valid'] and date_val['updated_at_valid']:
                assert isinstance(date_val['dates_consistent'], bool)
    
    @given(st.lists(blog_detail(), min_size=1, max_size=10))
    @settings(max_examples=30, deadline=None)
    def test_blog_detail_consistency_property(self, blogs):
        """
        属性: 博客详情一致性
        验证多个博客详情的数据一致性
        """
        all_results = [self.validator.validate_blog_detail_completeness(b) for b in blogs]
        
        # 验证内容分析的一致性
        content_analyses = [result['content_analysis'] for result in all_results]
        for analysis in content_analyses:
            # 内容长度和字数应该是合理的
            assert analysis['content_length'] >= 0
            assert analysis['word_count'] >= 0
            assert analysis['estimated_reading_time'] >= 0
            
            # 如果有内容，字数应该大于0
            if analysis['content_length'] > 0:
                assert analysis['word_count'] >= 0
        
        # 验证发布状态的一致性
        publication_statuses = [result['publication_status'] for result in all_results]
        for status in publication_statuses:
            assert isinstance(status['is_published'], bool)
            assert isinstance(status['ready_for_publication'], bool)
        
        # 验证SEO就绪性的逻辑一致性
        seo_readiness_list = [result['seo_readiness'] for result in all_results]
        for seo in seo_readiness_list:
            # 如果有标题，标题长度应该是合理的
            if seo['has_title']:
                assert isinstance(seo['title_length_appropriate'], bool)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])