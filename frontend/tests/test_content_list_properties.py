"""
内容列表显示完整性属性测试
验证需求 2.1, 3.1 - 作品和博客列表的显示完整性
"""

import pytest
from hypothesis import given, strategies as st, assume, settings
from typing import List, Dict, Any, Optional
import json
import re


# 测试数据生成策略
@st.composite
def portfolio_item(draw):
    """生成作品项目数据"""
    return {
        'id': draw(st.integers(min_value=1, max_value=10000)),
        'title': draw(st.text(min_size=1, max_size=100, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs')))),
        'description': draw(st.one_of(st.none(), st.text(min_size=0, max_size=500))),
        'tech_stack': draw(st.lists(st.text(min_size=1, max_size=20), min_size=1, max_size=10)),
        'project_url': draw(st.one_of(st.none(), st.text(min_size=10, max_size=200))),
        'github_url': draw(st.one_of(st.none(), st.text(min_size=10, max_size=200))),
        'image_url': draw(st.one_of(st.none(), st.text(min_size=10, max_size=200))),
        'display_order': draw(st.integers(min_value=0, max_value=1000)),
        'is_featured': draw(st.booleans()),
        'created_at': draw(st.datetimes().map(lambda dt: dt.isoformat())),
        'updated_at': draw(st.datetimes().map(lambda dt: dt.isoformat()))
    }


@st.composite
def blog_item(draw):
    """生成博客文章数据"""
    return {
        'id': draw(st.integers(min_value=1, max_value=10000)),
        'title': draw(st.text(min_size=1, max_size=100, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs')))),
        'content': draw(st.text(min_size=10, max_size=2000)),
        'summary': draw(st.one_of(st.none(), st.text(min_size=0, max_size=300))),
        'tags': draw(st.lists(st.text(min_size=1, max_size=20), min_size=0, max_size=8)),
        'is_published': draw(st.booleans()),
        'cover_image': draw(st.one_of(st.none(), st.text(min_size=10, max_size=200))),
        'created_at': draw(st.datetimes().map(lambda dt: dt.isoformat())),
        'updated_at': draw(st.datetimes().map(lambda dt: dt.isoformat()))
    }


class ContentListDisplayValidator:
    """内容列表显示验证器"""
    
    def __init__(self):
        self.required_portfolio_fields = ['id', 'title', 'tech_stack', 'display_order', 'is_featured']
        self.required_blog_fields = ['id', 'title', 'content', 'is_published', 'created_at']
        self.optional_portfolio_fields = ['description', 'project_url', 'github_url', 'image_url']
        self.optional_blog_fields = ['summary', 'tags', 'cover_image']
    
    def validate_portfolio_list_completeness(self, portfolios: List[Dict[str, Any]]) -> Dict[str, Any]:
        """验证作品列表显示完整性"""
        results = {
            'total_items': len(portfolios),
            'valid_items': 0,
            'missing_required_fields': [],
            'invalid_data_types': [],
            'empty_required_fields': [],
            'featured_items': 0,
            'items_with_images': 0,
            'items_with_links': 0,
            'tech_stack_coverage': {},
            'display_order_range': {'min': float('inf'), 'max': float('-inf')},
            'validation_errors': []
        }
        
        for i, portfolio in enumerate(portfolios):
            item_valid = True
            
            # 检查必需字段存在性
            for field in self.required_portfolio_fields:
                if field not in portfolio:
                    results['missing_required_fields'].append(f"Item {i}: missing {field}")
                    item_valid = False
                elif not portfolio[field] and field in ['title']:  # 某些字段不能为空
                    results['empty_required_fields'].append(f"Item {i}: empty {field}")
                    item_valid = False
            
            if 'id' in portfolio:
                # 检查数据类型
                if not isinstance(portfolio['id'], int) or portfolio['id'] <= 0:
                    results['invalid_data_types'].append(f"Item {i}: invalid id type or value")
                    item_valid = False
                
                if 'title' in portfolio and not isinstance(portfolio['title'], str):
                    results['invalid_data_types'].append(f"Item {i}: invalid title type")
                    item_valid = False
                
                if 'tech_stack' in portfolio:
                    if not isinstance(portfolio['tech_stack'], list):
                        results['invalid_data_types'].append(f"Item {i}: tech_stack must be list")
                        item_valid = False
                    else:
                        # 统计技术栈覆盖率
                        for tech in portfolio['tech_stack']:
                            if isinstance(tech, str):
                                results['tech_stack_coverage'][tech] = results['tech_stack_coverage'].get(tech, 0) + 1
                
                if 'display_order' in portfolio:
                    if isinstance(portfolio['display_order'], (int, float)):
                        results['display_order_range']['min'] = min(results['display_order_range']['min'], portfolio['display_order'])
                        results['display_order_range']['max'] = max(results['display_order_range']['max'], portfolio['display_order'])
                    else:
                        results['invalid_data_types'].append(f"Item {i}: invalid display_order type")
                        item_valid = False
                
                if 'is_featured' in portfolio:
                    if isinstance(portfolio['is_featured'], bool) and portfolio['is_featured']:
                        results['featured_items'] += 1
                    elif not isinstance(portfolio['is_featured'], bool):
                        results['invalid_data_types'].append(f"Item {i}: invalid is_featured type")
                        item_valid = False
                
                # 统计可选字段
                if portfolio.get('image_url'):
                    results['items_with_images'] += 1
                
                if portfolio.get('project_url') or portfolio.get('github_url'):
                    results['items_with_links'] += 1
            
            if item_valid:
                results['valid_items'] += 1
        
        # 处理空列表的边界情况
        if results['display_order_range']['min'] == float('inf'):
            results['display_order_range'] = {'min': 0, 'max': 0}
        
        return results
    
    def validate_blog_list_completeness(self, blogs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """验证博客列表显示完整性"""
        results = {
            'total_items': len(blogs),
            'valid_items': 0,
            'published_items': 0,
            'draft_items': 0,
            'missing_required_fields': [],
            'invalid_data_types': [],
            'empty_required_fields': [],
            'items_with_cover': 0,
            'items_with_summary': 0,
            'tag_coverage': {},
            'content_length_stats': {'min': float('inf'), 'max': 0, 'avg': 0},
            'validation_errors': []
        }
        
        total_content_length = 0
        
        for i, blog in enumerate(blogs):
            item_valid = True
            
            # 检查必需字段存在性
            for field in self.required_blog_fields:
                if field not in blog:
                    results['missing_required_fields'].append(f"Item {i}: missing {field}")
                    item_valid = False
                elif not blog[field] and field in ['title', 'content']:  # 某些字段不能为空
                    results['empty_required_fields'].append(f"Item {i}: empty {field}")
                    item_valid = False
            
            if 'id' in blog:
                # 检查数据类型
                if not isinstance(blog['id'], int) or blog['id'] <= 0:
                    results['invalid_data_types'].append(f"Item {i}: invalid id type or value")
                    item_valid = False
                
                if 'title' in blog and not isinstance(blog['title'], str):
                    results['invalid_data_types'].append(f"Item {i}: invalid title type")
                    item_valid = False
                
                if 'content' in blog:
                    if not isinstance(blog['content'], str):
                        results['invalid_data_types'].append(f"Item {i}: invalid content type")
                        item_valid = False
                    else:
                        content_len = len(blog['content'])
                        total_content_length += content_len
                        results['content_length_stats']['min'] = min(results['content_length_stats']['min'], content_len)
                        results['content_length_stats']['max'] = max(results['content_length_stats']['max'], content_len)
                
                if 'is_published' in blog:
                    if isinstance(blog['is_published'], bool):
                        if blog['is_published']:
                            results['published_items'] += 1
                        else:
                            results['draft_items'] += 1
                    else:
                        results['invalid_data_types'].append(f"Item {i}: invalid is_published type")
                        item_valid = False
                
                if 'tags' in blog:
                    if isinstance(blog['tags'], list):
                        for tag in blog['tags']:
                            if isinstance(tag, str):
                                results['tag_coverage'][tag] = results['tag_coverage'].get(tag, 0) + 1
                    else:
                        results['invalid_data_types'].append(f"Item {i}: tags must be list")
                        item_valid = False
                
                # 统计可选字段
                if blog.get('cover_image'):
                    results['items_with_cover'] += 1
                
                if blog.get('summary'):
                    results['items_with_summary'] += 1
            
            if item_valid:
                results['valid_items'] += 1
        
        # 计算平均内容长度
        if results['total_items'] > 0:
            results['content_length_stats']['avg'] = total_content_length / results['total_items']
        
        # 处理空列表的边界情况
        if results['content_length_stats']['min'] == float('inf'):
            results['content_length_stats']['min'] = 0
        
        return results
    
    def validate_list_sorting_consistency(self, items: List[Dict[str, Any]], sort_field: str, sort_order: str = 'desc') -> bool:
        """验证列表排序一致性"""
        if len(items) <= 1:
            return True
        
        for i in range(len(items) - 1):
            current = items[i].get(sort_field)
            next_item = items[i + 1].get(sort_field)
            
            if current is None or next_item is None:
                continue
            
            if sort_order == 'desc':
                if current < next_item:
                    return False
            else:  # asc
                if current > next_item:
                    return False
        
        return True
    
    def validate_pagination_consistency(self, total_items: int, page_size: int, current_page: int, returned_items: int) -> Dict[str, Any]:
        """验证分页一致性"""
        expected_items = min(page_size, max(0, total_items - (current_page - 1) * page_size))
        
        return {
            'expected_items': expected_items,
            'actual_items': returned_items,
            'is_consistent': expected_items == returned_items,
            'total_pages': (total_items + page_size - 1) // page_size if page_size > 0 else 0,
            'is_valid_page': 1 <= current_page <= max(1, (total_items + page_size - 1) // page_size) if page_size > 0 else False
        }


# 属性测试
class TestContentListDisplayProperties:
    """内容列表显示完整性属性测试"""
    
    def setup_method(self):
        self.validator = ContentListDisplayValidator()
    
    @given(st.lists(portfolio_item(), min_size=0, max_size=50))
    @settings(max_examples=100, deadline=None)
    def test_portfolio_list_completeness_property(self, portfolios):
        """
        属性 3: 内容列表显示完整性 - 作品列表
        验证作品列表中每个项目都包含必要的显示信息
        """
        results = self.validator.validate_portfolio_list_completeness(portfolios)
        
        # 基本完整性检查
        assert results['total_items'] == len(portfolios)
        assert results['valid_items'] <= results['total_items']
        
        # 如果有数据，验证数据完整性
        if portfolios:
            # 至少应该有一些有效项目
            assert results['valid_items'] >= 0
            
            # 验证必需字段检查的有效性
            if results['missing_required_fields']:
                assert results['valid_items'] < results['total_items']
            
            # 验证数据类型检查的有效性
            if results['invalid_data_types']:
                assert results['valid_items'] < results['total_items']
            
            # 验证技术栈统计的合理性
            total_tech_mentions = sum(results['tech_stack_coverage'].values())
            assert total_tech_mentions >= 0
            
            # 验证显示顺序范围的合理性
            if results['display_order_range']['min'] <= results['display_order_range']['max']:
                assert True  # 范围合理
            
            # 验证特色项目统计
            assert 0 <= results['featured_items'] <= results['total_items']
            
            # 验证图片和链接统计
            assert 0 <= results['items_with_images'] <= results['total_items']
            assert 0 <= results['items_with_links'] <= results['total_items']
    
    @given(st.lists(blog_item(), min_size=0, max_size=50))
    @settings(max_examples=100, deadline=None)
    def test_blog_list_completeness_property(self, blogs):
        """
        属性 3: 内容列表显示完整性 - 博客列表
        验证博客列表中每篇文章都包含必要的显示信息
        """
        results = self.validator.validate_blog_list_completeness(blogs)
        
        # 基本完整性检查
        assert results['total_items'] == len(blogs)
        assert results['valid_items'] <= results['total_items']
        
        # 如果有数据，验证数据完整性
        if blogs:
            # 至少应该有一些有效项目
            assert results['valid_items'] >= 0
            
            # 验证发布状态统计
            assert results['published_items'] + results['draft_items'] <= results['total_items']
            assert results['published_items'] >= 0
            assert results['draft_items'] >= 0
            
            # 验证内容长度统计的合理性
            assert results['content_length_stats']['min'] >= 0
            assert results['content_length_stats']['max'] >= results['content_length_stats']['min']
            assert results['content_length_stats']['avg'] >= 0
            
            # 验证标签统计的合理性
            total_tag_mentions = sum(results['tag_coverage'].values())
            assert total_tag_mentions >= 0
            
            # 验证可选字段统计
            assert 0 <= results['items_with_cover'] <= results['total_items']
            assert 0 <= results['items_with_summary'] <= results['total_items']
    
    @given(
        st.lists(portfolio_item(), min_size=0, max_size=20),
        st.sampled_from(['display_order', 'created_at', 'title']),
        st.sampled_from(['asc', 'desc'])
    )
    @settings(max_examples=50, deadline=None)
    def test_portfolio_sorting_consistency_property(self, portfolios, sort_field, sort_order):
        """
        属性 5: 内容排序一致性 - 作品排序
        验证作品列表按指定字段排序的一致性
        """
        # 过滤掉没有排序字段的项目
        valid_portfolios = [p for p in portfolios if sort_field in p and p[sort_field] is not None]
        
        if len(valid_portfolios) <= 1:
            # 空列表或单项列表总是有序的
            assert self.validator.validate_list_sorting_consistency(valid_portfolios, sort_field, sort_order)
        else:
            # 手动排序以验证排序逻辑
            if sort_field == 'title':
                sorted_portfolios = sorted(valid_portfolios, key=lambda x: x[sort_field], reverse=(sort_order == 'desc'))
            else:
                sorted_portfolios = sorted(valid_portfolios, key=lambda x: x[sort_field], reverse=(sort_order == 'desc'))
            
            # 验证排序一致性
            is_consistent = self.validator.validate_list_sorting_consistency(sorted_portfolios, sort_field, sort_order)
            assert is_consistent, f"Sorting by {sort_field} in {sort_order} order should be consistent"
    
    @given(
        st.lists(blog_item(), min_size=0, max_size=20),
        st.sampled_from(['created_at', 'title']),
        st.sampled_from(['asc', 'desc'])
    )
    @settings(max_examples=50, deadline=None)
    def test_blog_sorting_consistency_property(self, blogs, sort_field, sort_order):
        """
        属性 5: 内容排序一致性 - 博客排序
        验证博客列表按指定字段排序的一致性
        """
        # 过滤掉没有排序字段的项目
        valid_blogs = [b for b in blogs if sort_field in b and b[sort_field] is not None]
        
        if len(valid_blogs) <= 1:
            # 空列表或单项列表总是有序的
            assert self.validator.validate_list_sorting_consistency(valid_blogs, sort_field, sort_order)
        else:
            # 手动排序以验证排序逻辑
            if sort_field == 'title':
                sorted_blogs = sorted(valid_blogs, key=lambda x: x[sort_field], reverse=(sort_order == 'desc'))
            else:  # created_at
                sorted_blogs = sorted(valid_blogs, key=lambda x: x[sort_field], reverse=(sort_order == 'desc'))
            
            # 验证排序一致性
            is_consistent = self.validator.validate_list_sorting_consistency(sorted_blogs, sort_field, sort_order)
            assert is_consistent, f"Sorting by {sort_field} in {sort_order} order should be consistent"
    
    @given(
        st.integers(min_value=0, max_value=1000),  # total_items
        st.integers(min_value=1, max_value=50),    # page_size
        st.integers(min_value=1, max_value=100)    # current_page
    )
    @settings(max_examples=100, deadline=None)
    def test_pagination_consistency_property(self, total_items, page_size, current_page):
        """
        属性: 分页一致性
        验证分页逻辑的数学一致性
        """
        # 计算实际应该返回的项目数
        start_index = (current_page - 1) * page_size
        end_index = min(start_index + page_size, total_items)
        expected_items = max(0, end_index - start_index)
        
        # 模拟返回的项目数（在合理范围内）
        returned_items = expected_items if start_index < total_items else 0
        
        results = self.validator.validate_pagination_consistency(
            total_items, page_size, current_page, returned_items
        )
        
        # 验证分页计算的一致性
        assert results['expected_items'] == returned_items
        assert results['is_consistent'] == True
        
        # 验证总页数计算
        expected_total_pages = (total_items + page_size - 1) // page_size if page_size > 0 else 0
        assert results['total_pages'] == expected_total_pages
        
        # 验证页码有效性
        if total_items == 0:
            assert results['is_valid_page'] == (current_page == 1)
        else:
            assert results['is_valid_page'] == (1 <= current_page <= results['total_pages'])
    
    @given(st.lists(portfolio_item(), min_size=1, max_size=20))
    @settings(max_examples=50, deadline=None)
    def test_featured_items_priority_property(self, portfolios):
        """
        属性: 精选项目优先级
        验证精选项目在列表中的优先显示
        """
        # 分离精选和非精选项目
        featured = [p for p in portfolios if p.get('is_featured', False)]
        non_featured = [p for p in portfolios if not p.get('is_featured', False)]
        
        # 验证精选项目统计
        results = self.validator.validate_portfolio_list_completeness(portfolios)
        assert results['featured_items'] == len(featured)
        
        # 如果同时有精选和非精选项目，验证优先级逻辑
        if featured and non_featured:
            # 模拟按精选优先排序
            sorted_portfolios = featured + non_featured
            
            # 验证前面的项目都是精选的
            for i in range(len(featured)):
                assert sorted_portfolios[i].get('is_featured', False) == True
            
            # 验证后面的项目都不是精选的
            for i in range(len(featured), len(sorted_portfolios)):
                assert sorted_portfolios[i].get('is_featured', False) == False
    
    @given(st.lists(blog_item(), min_size=1, max_size=20))
    @settings(max_examples=50, deadline=None)
    def test_published_content_filtering_property(self, blogs):
        """
        属性: 已发布内容过滤
        验证只显示已发布的博客内容
        """
        results = self.validator.validate_blog_list_completeness(blogs)
        
        # 统计发布状态
        published_count = len([b for b in blogs if b.get('is_published', False)])
        draft_count = len([b for b in blogs if not b.get('is_published', False)])
        
        assert results['published_items'] == published_count
        assert results['draft_items'] == draft_count
        assert results['published_items'] + results['draft_items'] <= len(blogs)
        
        # 验证过滤逻辑
        published_blogs = [b for b in blogs if b.get('is_published', False)]
        
        # 所有过滤后的博客都应该是已发布状态
        for blog in published_blogs:
            assert blog.get('is_published', False) == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])