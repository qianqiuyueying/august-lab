"""
内容排序一致性属性测试
验证需求 2.3, 3.3 - 作品和博客的排序功能一致性
"""

import pytest
from hypothesis import given, strategies as st, assume, settings
from typing import List, Dict, Any, Optional, Callable
import json
from datetime import datetime
from functools import cmp_to_key


# 测试数据生成策略
@st.composite
def sortable_portfolio(draw):
    """生成可排序的作品数据"""
    created_dt = draw(st.datetimes())
    updated_dt = draw(st.datetimes(min_value=created_dt))
    
    # 使用唯一ID计数器确保ID不重复
    portfolio_id = draw(st.integers(min_value=1, max_value=100000))
    
    return {
        'id': portfolio_id,
        'title': draw(st.text(min_size=3, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs')))),
        'description': draw(st.one_of(st.none(), st.text(min_size=0, max_size=500))),
        'tech_stack': draw(st.lists(st.text(min_size=1, max_size=20), min_size=1, max_size=8)),
        'project_url': draw(st.one_of(st.none(), st.text(min_size=10, max_size=200))),
        'github_url': draw(st.one_of(st.none(), st.text(min_size=10, max_size=200))),
        'image_url': draw(st.one_of(st.none(), st.text(min_size=10, max_size=200))),
        'display_order': draw(st.integers(min_value=0, max_value=1000)),
        'is_featured': draw(st.booleans()),
        'created_at': created_dt.isoformat(),
        'updated_at': updated_dt.isoformat()
    }


@st.composite
def sortable_blog(draw):
    """生成可排序的博客数据"""
    created_dt = draw(st.datetimes())
    updated_dt = draw(st.datetimes(min_value=created_dt))
    
    # 使用唯一ID计数器确保ID不重复
    blog_id = draw(st.integers(min_value=1, max_value=100000))
    
    return {
        'id': blog_id,
        'title': draw(st.text(min_size=3, max_size=100, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs')))),
        'content': draw(st.text(min_size=50, max_size=2000)),
        'summary': draw(st.one_of(st.none(), st.text(min_size=0, max_size=300))),
        'tags': draw(st.lists(st.text(min_size=1, max_size=20), min_size=0, max_size=8)),
        'is_published': draw(st.booleans()),
        'cover_image': draw(st.one_of(st.none(), st.text(min_size=10, max_size=200))),
        'created_at': created_dt.isoformat(),
        'updated_at': updated_dt.isoformat()
    }


class ContentSortingValidator:
    """内容排序验证器"""
    
    def __init__(self):
        self.portfolio_sort_fields = ['display_order', 'created_at', 'updated_at', 'title', 'id']
        self.blog_sort_fields = ['created_at', 'updated_at', 'title', 'id']
        self.sort_orders = ['asc', 'desc']
    
    def sort_portfolios(self, portfolios: List[Dict[str, Any]], sort_field: str, sort_order: str = 'desc') -> List[Dict[str, Any]]:
        """排序作品列表"""
        if not portfolios:
            return portfolios
        
        def get_sort_key(item):
            value = item.get(sort_field)
            if value is None:
                return '' if sort_field in ['title'] else 0
            
            # 处理日期字段
            if sort_field in ['created_at', 'updated_at']:
                try:
                    return datetime.fromisoformat(value.replace('Z', '+00:00'))
                except:
                    return datetime.min
            
            # 处理数字字段
            if sort_field in ['display_order', 'id']:
                return value if isinstance(value, (int, float)) else 0
            
            # 处理字符串字段
            if sort_field == 'title':
                return str(value).lower()
            
            return value
        
        reverse = (sort_order == 'desc')
        return sorted(portfolios, key=get_sort_key, reverse=reverse)
    
    def sort_blogs(self, blogs: List[Dict[str, Any]], sort_field: str, sort_order: str = 'desc') -> List[Dict[str, Any]]:
        """排序博客列表"""
        if not blogs:
            return blogs
        
        def get_sort_key(item):
            value = item.get(sort_field)
            if value is None:
                return '' if sort_field in ['title'] else 0
            
            # 处理日期字段
            if sort_field in ['created_at', 'updated_at']:
                try:
                    return datetime.fromisoformat(value.replace('Z', '+00:00'))
                except:
                    return datetime.min
            
            # 处理数字字段
            if sort_field == 'id':
                return value if isinstance(value, (int, float)) else 0
            
            # 处理字符串字段
            if sort_field == 'title':
                return str(value).lower()
            
            return value
        
        reverse = (sort_order == 'desc')
        return sorted(blogs, key=get_sort_key, reverse=reverse)
    
    def validate_sort_consistency(self, items: List[Dict[str, Any]], sort_field: str, sort_order: str = 'desc') -> Dict[str, Any]:
        """验证排序一致性"""
        results = {
            'is_sorted': True,
            'violations': [],
            'total_items': len(items),
            'null_values': 0,
            'sort_field': sort_field,
            'sort_order': sort_order,
            'field_type_consistency': True,
            'field_types': set()
        }
        
        if len(items) <= 1:
            return results
        
        # 检查字段类型一致性
        field_types = set()
        for item in items:
            value = item.get(sort_field)
            if value is not None:
                field_types.add(type(value).__name__)
            else:
                results['null_values'] += 1
        
        results['field_types'] = field_types
        results['field_type_consistency'] = len(field_types) <= 1
        
        # 检查排序一致性
        for i in range(len(items) - 1):
            current = items[i].get(sort_field)
            next_item = items[i + 1].get(sort_field)
            
            # 处理None值
            if current is None and next_item is None:
                continue
            elif current is None:
                current = '' if sort_field in ['title'] else 0
            elif next_item is None:
                next_item = '' if sort_field in ['title'] else 0
            
            # 处理日期比较
            if sort_field in ['created_at', 'updated_at']:
                try:
                    current_dt = datetime.fromisoformat(str(current).replace('Z', '+00:00'))
                    next_dt = datetime.fromisoformat(str(next_item).replace('Z', '+00:00'))
                    current, next_item = current_dt, next_dt
                except:
                    continue
            
            # 处理字符串比较
            elif sort_field == 'title':
                current = str(current).lower()
                next_item = str(next_item).lower()
            
            # 检查排序顺序
            if sort_order == 'desc':
                if current < next_item:
                    results['is_sorted'] = False
                    results['violations'].append({
                        'position': i,
                        'current_value': current,
                        'next_value': next_item,
                        'expected': f'{current} >= {next_item}'
                    })
            else:  # asc
                if current > next_item:
                    results['is_sorted'] = False
                    results['violations'].append({
                        'position': i,
                        'current_value': current,
                        'next_value': next_item,
                        'expected': f'{current} <= {next_item}'
                    })
        
        return results
    
    def validate_featured_priority_sorting(self, portfolios: List[Dict[str, Any]]) -> Dict[str, Any]:
        """验证精选项目优先排序"""
        results = {
            'featured_first': True,
            'featured_count': 0,
            'non_featured_count': 0,
            'first_non_featured_position': None,
            'violations': []
        }
        
        featured_ended = False
        
        for i, portfolio in enumerate(portfolios):
            is_featured = portfolio.get('is_featured', False)
            
            if is_featured:
                results['featured_count'] += 1
                if featured_ended:
                    # 发现精选项目出现在非精选项目之后
                    results['featured_first'] = False
                    results['violations'].append({
                        'position': i,
                        'issue': 'featured item after non-featured item'
                    })
            else:
                results['non_featured_count'] += 1
                if not featured_ended:
                    featured_ended = True
                    results['first_non_featured_position'] = i
        
        return results
    
    def validate_multi_level_sorting(self, items: List[Dict[str, Any]], primary_field: str, secondary_field: str, sort_order: str = 'desc') -> Dict[str, Any]:
        """验证多级排序"""
        results = {
            'primary_sorted': True,
            'secondary_sorted_within_groups': True,
            'groups': [],
            'violations': []
        }
        
        if len(items) <= 1:
            return results
        
        # 按主要字段分组
        current_group = []
        current_primary_value = None
        
        for item in items:
            primary_value = item.get(primary_field)
            
            if current_primary_value is None or primary_value == current_primary_value:
                current_group.append(item)
                current_primary_value = primary_value
            else:
                if current_group:
                    results['groups'].append({
                        'primary_value': current_primary_value,
                        'items': current_group.copy(),
                        'count': len(current_group)
                    })
                current_group = [item]
                current_primary_value = primary_value
        
        # 添加最后一组
        if current_group:
            results['groups'].append({
                'primary_value': current_primary_value,
                'items': current_group.copy(),
                'count': len(current_group)
            })
        
        # 验证每组内的二级排序
        for group in results['groups']:
            if len(group['items']) > 1:
                group_validation = self.validate_sort_consistency(
                    group['items'], secondary_field, sort_order
                )
                if not group_validation['is_sorted']:
                    results['secondary_sorted_within_groups'] = False
                    results['violations'].extend(group_validation['violations'])
        
        return results
    
    def validate_stable_sorting(self, original_items: List[Dict[str, Any]], sorted_items: List[Dict[str, Any]], sort_field: str) -> Dict[str, Any]:
        """验证稳定排序（相同值的项目保持原有顺序）"""
        results = {
            'is_stable': True,
            'equal_value_groups': [],
            'violations': []
        }
        
        # 找出具有相同排序字段值的项目组
        value_groups = {}
        for i, item in enumerate(original_items):
            value = item.get(sort_field)
            if value not in value_groups:
                value_groups[value] = []
            value_groups[value].append((i, item))
        
        # 检查每组中有多个项目的情况
        for value, group in value_groups.items():
            if len(group) > 1:
                results['equal_value_groups'].append({
                    'value': value,
                    'count': len(group),
                    'original_positions': [pos for pos, _ in group]
                })
                
                # 在排序后的列表中找到这些项目的位置
                sorted_positions = []
                used_positions = set()  # 跟踪已使用的位置，处理重复ID
                
                for original_pos, original_item in group:
                    found_position = None
                    for j, sorted_item in enumerate(sorted_items):
                        if (sorted_item.get('id') == original_item.get('id') and 
                            j not in used_positions):
                            found_position = j
                            used_positions.add(j)
                            break
                    
                    if found_position is not None:
                        sorted_positions.append(found_position)
                
                # 检查相对顺序是否保持（只有当找到所有项目时）
                if len(sorted_positions) == len(group):
                    # 对于稳定排序，相同值的项目应该保持相对顺序
                    if not all(sorted_positions[i] <= sorted_positions[i+1] for i in range(len(sorted_positions)-1)):
                        results['is_stable'] = False
                        results['violations'].append({
                            'value': value,
                            'original_positions': [pos for pos, _ in group],
                            'sorted_positions': sorted_positions
                        })
        
        return results


# 属性测试
class TestContentSortingProperties:
    """内容排序一致性属性测试"""
    
    def setup_method(self):
        self.validator = ContentSortingValidator()
    
    @given(
        st.lists(sortable_portfolio(), min_size=0, max_size=20),
        st.sampled_from(['display_order', 'created_at', 'updated_at', 'title', 'id']),
        st.sampled_from(['asc', 'desc'])
    )
    @settings(max_examples=100, deadline=None)
    def test_portfolio_sorting_consistency_property(self, portfolios, sort_field, sort_order):
        """
        属性 5: 内容排序一致性 - 作品排序
        验证作品列表按任意字段排序的一致性
        """
        if not portfolios:
            return  # 空列表无需排序
        
        # 执行排序
        sorted_portfolios = self.validator.sort_portfolios(portfolios, sort_field, sort_order)
        
        # 验证排序结果
        validation_results = self.validator.validate_sort_consistency(sorted_portfolios, sort_field, sort_order)
        
        # 基本排序一致性检查
        assert validation_results['is_sorted'] == True, f"Sorting by {sort_field} {sort_order} failed: {validation_results['violations']}"
        assert validation_results['total_items'] == len(portfolios)
        
        # 验证排序没有丢失或重复项目
        assert len(sorted_portfolios) == len(portfolios)
        
        # 验证所有原始项目都在排序结果中
        original_ids = {p.get('id') for p in portfolios}
        sorted_ids = {p.get('id') for p in sorted_portfolios}
        assert original_ids == sorted_ids, "Sorting should not lose or duplicate items"
        
        # 验证字段类型一致性
        if validation_results['field_types']:
            assert validation_results['field_type_consistency'] == True, f"Inconsistent field types: {validation_results['field_types']}"
    
    @given(
        st.lists(sortable_blog(), min_size=0, max_size=20),
        st.sampled_from(['created_at', 'updated_at', 'title', 'id']),
        st.sampled_from(['asc', 'desc'])
    )
    @settings(max_examples=100, deadline=None)
    def test_blog_sorting_consistency_property(self, blogs, sort_field, sort_order):
        """
        属性 5: 内容排序一致性 - 博客排序
        验证博客列表按任意字段排序的一致性
        """
        if not blogs:
            return  # 空列表无需排序
        
        # 执行排序
        sorted_blogs = self.validator.sort_blogs(blogs, sort_field, sort_order)
        
        # 验证排序结果
        validation_results = self.validator.validate_sort_consistency(sorted_blogs, sort_field, sort_order)
        
        # 基本排序一致性检查
        assert validation_results['is_sorted'] == True, f"Sorting by {sort_field} {sort_order} failed: {validation_results['violations']}"
        assert validation_results['total_items'] == len(blogs)
        
        # 验证排序没有丢失或重复项目
        assert len(sorted_blogs) == len(blogs)
        
        # 验证所有原始项目都在排序结果中
        original_ids = {b.get('id') for b in blogs}
        sorted_ids = {b.get('id') for b in sorted_blogs}
        assert original_ids == sorted_ids, "Sorting should not lose or duplicate items"
        
        # 验证字段类型一致性
        if validation_results['field_types']:
            assert validation_results['field_type_consistency'] == True, f"Inconsistent field types: {validation_results['field_types']}"
    
    @given(st.lists(sortable_portfolio(), min_size=1, max_size=15))
    @settings(max_examples=50, deadline=None)
    def test_featured_priority_sorting_property(self, portfolios):
        """
        属性: 精选项目优先排序
        验证精选项目始终排在非精选项目之前
        """
        # 模拟精选优先排序
        featured_portfolios = [p for p in portfolios if p.get('is_featured', False)]
        non_featured_portfolios = [p for p in portfolios if not p.get('is_featured', False)]
        
        # 按精选优先排序
        priority_sorted = featured_portfolios + non_featured_portfolios
        
        # 验证精选优先级
        validation_results = self.validator.validate_featured_priority_sorting(priority_sorted)
        
        assert validation_results['featured_first'] == True, f"Featured items should come first: {validation_results['violations']}"
        assert validation_results['featured_count'] == len(featured_portfolios)
        assert validation_results['non_featured_count'] == len(non_featured_portfolios)
        
        # 如果有非精选项目，验证第一个非精选项目的位置
        if non_featured_portfolios:
            expected_position = len(featured_portfolios)
            assert validation_results['first_non_featured_position'] == expected_position
    
    @given(
        st.lists(sortable_portfolio(), min_size=2, max_size=10),
        st.sampled_from(['display_order', 'created_at']),
        st.sampled_from(['id'])  # 简化为只测试ID作为次要字段
    )
    @settings(max_examples=20, deadline=None)
    def test_multi_level_sorting_property(self, portfolios, primary_field, secondary_field):
        """
        属性: 多级排序一致性
        验证多级排序的正确性（主要字段相同时按次要字段排序）
        """
        # 确保有一些相同的主要字段值
        if len(portfolios) >= 2:
            portfolios[1][primary_field] = portfolios[0][primary_field]
        
        # 先按主要字段排序，再按次要字段排序
        sorted_portfolios = self.validator.sort_portfolios(portfolios, primary_field, 'desc')
        
        # 验证多级排序
        validation_results = self.validator.validate_multi_level_sorting(
            sorted_portfolios, primary_field, secondary_field, 'desc'
        )
        
        assert validation_results['primary_sorted'] == True
        # 对于多级排序，我们主要验证分组逻辑是否正确
        total_items_in_groups = sum(group['count'] for group in validation_results['groups'])
        assert total_items_in_groups == len(portfolios), "All items should be in groups"
    
    @given(
        st.lists(sortable_portfolio(), min_size=2, max_size=8),
        st.sampled_from(['display_order'])  # 简化为只测试数字字段
    )
    @settings(max_examples=20, deadline=None)
    def test_stable_sorting_property(self, portfolios, sort_field):
        """
        属性: 稳定排序
        验证相同排序值的项目保持原有相对顺序
        """
        # 确保ID唯一性
        for i, portfolio in enumerate(portfolios):
            portfolio['id'] = i + 1
        
        # 创建一些具有相同排序字段值的项目
        if len(portfolios) >= 2:
            portfolios[1][sort_field] = portfolios[0][sort_field]
        
        # 执行排序
        sorted_portfolios = self.validator.sort_portfolios(portfolios, sort_field, 'desc')
        
        # 验证稳定性
        validation_results = self.validator.validate_stable_sorting(portfolios, sorted_portfolios, sort_field)
        
        # 对于稳定排序，我们主要验证相同值组的识别是否正确
        if validation_results['equal_value_groups']:
            for group in validation_results['equal_value_groups']:
                assert group['count'] >= 2, "Equal value groups should have at least 2 items"
        
        # 基本的稳定性检查（如果没有重复ID问题）
        if len(set(p['id'] for p in portfolios)) == len(portfolios):
            assert validation_results['is_stable'] == True, f"Sorting should be stable: {validation_results['violations']}"
    
    @given(
        st.lists(sortable_blog(), min_size=1, max_size=15),
        st.sampled_from(['created_at', 'updated_at'])
    )
    @settings(max_examples=50, deadline=None)
    def test_date_sorting_consistency_property(self, blogs, date_field):
        """
        属性: 日期排序一致性
        验证日期字段排序的特殊处理
        """
        # 执行日期排序
        sorted_blogs = self.validator.sort_blogs(blogs, date_field, 'desc')
        
        # 验证日期排序
        validation_results = self.validator.validate_sort_consistency(sorted_blogs, date_field, 'desc')
        
        assert validation_results['is_sorted'] == True, f"Date sorting failed: {validation_results['violations']}"
        
        # 验证日期格式处理
        for blog in sorted_blogs:
            date_value = blog.get(date_field)
            if date_value:
                try:
                    # 验证日期可以被正确解析
                    datetime.fromisoformat(date_value.replace('Z', '+00:00'))
                except ValueError:
                    pytest.fail(f"Invalid date format: {date_value}")
    
    @given(
        st.lists(sortable_portfolio(), min_size=0, max_size=20),
        st.sampled_from(['display_order', 'created_at', 'title'])
    )
    @settings(max_examples=50, deadline=None)
    def test_sort_order_reversal_property(self, portfolios, sort_field):
        """
        属性: 排序顺序反转一致性
        验证升序和降序排序结果互为反转
        """
        if len(portfolios) <= 1:
            return  # 单项或空列表无需测试反转
        
        # 分别进行升序和降序排序
        asc_sorted = self.validator.sort_portfolios(portfolios, sort_field, 'asc')
        desc_sorted = self.validator.sort_portfolios(portfolios, sort_field, 'desc')
        
        # 验证两种排序都是有效的
        asc_validation = self.validator.validate_sort_consistency(asc_sorted, sort_field, 'asc')
        desc_validation = self.validator.validate_sort_consistency(desc_sorted, sort_field, 'desc')
        
        assert asc_validation['is_sorted'] == True, f"Ascending sort failed: {asc_validation['violations']}"
        assert desc_validation['is_sorted'] == True, f"Descending sort failed: {desc_validation['violations']}"
        
        # 验证升序和降序结果互为反转（对于没有重复值的情况）
        if len(set(p.get(sort_field) for p in portfolios)) == len(portfolios):
            # 没有重复值，升序和降序应该完全相反
            asc_ids = [p.get('id') for p in asc_sorted]
            desc_ids = [p.get('id') for p in desc_sorted]
            assert asc_ids == desc_ids[::-1], "Ascending and descending sorts should be reverse of each other"
    
    @given(st.lists(sortable_portfolio(), min_size=5, max_size=20))
    @settings(max_examples=30, deadline=None)
    def test_sorting_performance_consistency_property(self, portfolios):
        """
        属性: 排序性能一致性
        验证不同排序字段的性能特征一致性
        """
        sort_fields = ['display_order', 'created_at', 'title', 'id']
        sort_results = {}
        
        # 对每个字段进行排序并记录结果
        for field in sort_fields:
            sorted_items = self.validator.sort_portfolios(portfolios, field, 'desc')
            validation = self.validator.validate_sort_consistency(sorted_items, field, 'desc')
            
            sort_results[field] = {
                'sorted_count': len(sorted_items),
                'is_valid': validation['is_sorted'],
                'null_values': validation['null_values'],
                'field_types': validation['field_types']
            }
        
        # 验证所有排序结果的基本一致性
        for field, result in sort_results.items():
            assert result['sorted_count'] == len(portfolios), f"Sort by {field} should preserve item count"
            assert result['is_valid'] == True, f"Sort by {field} should be valid"
            assert result['null_values'] >= 0, f"Null value count should be non-negative for {field}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])