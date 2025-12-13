"""
Portfolio Management Functionality Property Tests

Tests for portfolio management CRUD operations, form validation,
and data integrity in the admin interface.
"""

import pytest
from hypothesis import given, strategies as st, assume
from typing import Dict, Any, List, Optional
import re
from datetime import datetime, date


class PortfolioValidator:
    """Portfolio data validation and management logic"""
    
    @staticmethod
    def validate_portfolio_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate portfolio form data"""
        errors = {}
        
        # Title validation
        title = data.get('title', '').strip()
        if not title:
            errors['title'] = 'Title is required'
        elif len(title) < 2 or len(title) > 100:
            errors['title'] = 'Title must be 2-100 characters'
        
        # Description validation
        description = data.get('description', '').strip()
        if not description:
            errors['description'] = 'Description is required'
        elif len(description) < 10 or len(description) > 500:
            errors['description'] = 'Description must be 10-500 characters'
        
        # Content validation
        content = data.get('content', '').strip()
        if not content:
            errors['content'] = 'Content is required'
        
        # URL validation
        project_url = data.get('project_url', '').strip()
        if project_url and not re.match(r'^https?://.+', project_url):
            errors['project_url'] = 'Invalid URL format'
        
        github_url = data.get('github_url', '').strip()
        if github_url and not re.match(r'^https?://(www\.)?github\.com/.+', github_url):
            errors['github_url'] = 'Invalid GitHub URL format'
        
        return errors
    
    @staticmethod
    def process_tech_stack(tech_stack: List[str]) -> List[str]:
        """Process and validate tech stack"""
        if not tech_stack:
            return []
        
        # Remove duplicates and empty strings
        processed = []
        seen = set()
        for tech in tech_stack:
            tech = tech.strip()
            if tech and tech not in seen:
                processed.append(tech)
                seen.add(tech)
        
        return processed
    
    @staticmethod
    def process_timeline(timeline: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Process and validate development timeline"""
        if not timeline:
            return []
        
        processed = []
        for item in timeline:
            date_str = item.get('date', '').strip()
            description = item.get('description', '').strip()
            
            if date_str and description:
                # Validate date format
                try:
                    datetime.strptime(date_str, '%Y-%m-%d')
                    processed.append({
                        'date': date_str,
                        'description': description
                    })
                except ValueError:
                    continue
        
        # Sort by date
        processed.sort(key=lambda x: x['date'])
        return processed
    
    @staticmethod
    def apply_filters(portfolios: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Apply search and filter criteria"""
        result = portfolios.copy()
        
        # Search filter
        search_query = filters.get('search', '').lower().strip()
        if search_query:
            result = [
                p for p in result
                if search_query in p.get('title', '').lower() or
                   search_query in p.get('description', '').lower()
            ]
        
        # Status filter
        status_filter = filters.get('status', '')
        if status_filter == 'featured':
            result = [p for p in result if p.get('is_featured', False)]
        elif status_filter == 'normal':
            result = [p for p in result if not p.get('is_featured', False)]
        
        return result
    
    @staticmethod
    def sort_portfolios(portfolios: List[Dict[str, Any]], sort_by: str, order: str = 'desc') -> List[Dict[str, Any]]:
        """Sort portfolios by specified criteria"""
        if not portfolios:
            return []
        
        def get_sort_key(portfolio: Dict[str, Any]) -> Any:
            value = portfolio.get(sort_by, '')
            if isinstance(value, str):
                return value.lower()
            return value
        
        reverse = order == 'desc'
        return sorted(portfolios, key=get_sort_key, reverse=reverse)


# Test data generators
@st.composite
def portfolio_data(draw):
    """Generate valid portfolio data"""
    return {
        'id': draw(st.integers(min_value=1, max_value=1000)),
        'title': draw(st.text(min_size=2, max_size=100, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs')))),
        'description': draw(st.text(min_size=10, max_size=500, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs', 'Po')))),
        'content': draw(st.text(min_size=1, max_size=2000, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs', 'Po'))).filter(lambda x: x.strip())),
        'project_url': draw(st.one_of(
            st.just(''),
            st.text(min_size=10, max_size=200).map(lambda x: f'https://example.com/{x.replace(" ", "-")}')
        )),
        'github_url': draw(st.one_of(
            st.just(''),
            st.text(min_size=5, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))).map(
                lambda x: f'https://github.com/user/{x}'
            )
        )),
        'image_url': draw(st.one_of(
            st.just(''),
            st.text(min_size=10, max_size=200).map(lambda x: f'https://example.com/images/{x}.jpg')
        )),
        'tech_stack': draw(st.lists(
            st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
            min_size=0, max_size=10
        )),
        'development_timeline': draw(st.lists(
            st.fixed_dictionaries({
                'date': st.dates(min_value=date(2020, 1, 1), max_value=date(2024, 12, 31)).map(str),
                'description': st.text(min_size=5, max_size=100, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs')))
            }),
            min_size=0, max_size=5
        )),
        'is_featured': draw(st.booleans()),
        'sort_order': draw(st.integers(min_value=0, max_value=999)),
        'created_at': draw(st.datetimes(min_value=datetime(2020, 1, 1), max_value=datetime(2024, 12, 31))).isoformat(),
        'updated_at': draw(st.datetimes(min_value=datetime(2020, 1, 1), max_value=datetime(2024, 12, 31))).isoformat()
    }


@st.composite
def invalid_portfolio_data(draw):
    """Generate invalid portfolio data for validation testing"""
    invalid_type = draw(st.sampled_from(['empty_title', 'long_title', 'short_description', 'invalid_url', 'invalid_github']))
    
    base_data = {
        'title': 'Valid Title',
        'description': 'This is a valid description with enough characters',
        'content': 'Valid content',
        'project_url': 'https://example.com',
        'github_url': 'https://github.com/user/repo',
        'tech_stack': ['Vue.js', 'TypeScript'],
        'is_featured': False,
        'sort_order': 0
    }
    
    if invalid_type == 'empty_title':
        base_data['title'] = ''
    elif invalid_type == 'long_title':
        base_data['title'] = 'x' * 101
    elif invalid_type == 'short_description':
        base_data['description'] = 'short'
    elif invalid_type == 'invalid_url':
        base_data['project_url'] = 'not-a-url'
    elif invalid_type == 'invalid_github':
        base_data['github_url'] = 'https://example.com/not-github'
    
    return base_data


class TestPortfolioManagementProperties:
    """Property tests for portfolio management functionality"""
    
    @given(portfolio_data())
    def test_valid_portfolio_validation_passes(self, portfolio):
        """Valid portfolio data should pass validation"""
        validator = PortfolioValidator()
        errors = validator.validate_portfolio_data(portfolio)
        
        # Should have no validation errors for valid data
        assert len(errors) == 0
    
    @given(invalid_portfolio_data())
    def test_invalid_portfolio_validation_fails(self, portfolio):
        """Invalid portfolio data should fail validation"""
        validator = PortfolioValidator()
        errors = validator.validate_portfolio_data(portfolio)
        
        # Should have at least one validation error
        assert len(errors) > 0
    
    @given(st.lists(st.text(min_size=1, max_size=20), min_size=0, max_size=15))
    def test_tech_stack_processing_removes_duplicates(self, tech_list):
        """Tech stack processing should remove duplicates and empty strings"""
        validator = PortfolioValidator()
        
        # Add some duplicates and empty strings
        test_list = tech_list + tech_list[:3] + ['', '  ', tech_list[0] if tech_list else 'test']
        
        processed = validator.process_tech_stack(test_list)
        
        # Should not contain duplicates
        assert len(processed) == len(set(processed))
        
        # Should not contain empty strings
        assert all(tech.strip() for tech in processed)
        
        # Should preserve order of first occurrence
        seen = set()
        for tech in processed:
            assert tech not in seen
            seen.add(tech)
    
    @given(st.lists(
        st.fixed_dictionaries({
            'date': st.dates(min_value=date(2020, 1, 1), max_value=date(2024, 12, 31)).map(str),
            'description': st.text(min_size=1, max_size=100)
        }),
        min_size=0, max_size=10
    ))
    def test_timeline_processing_sorts_by_date(self, timeline):
        """Timeline processing should sort entries by date"""
        validator = PortfolioValidator()
        processed = validator.process_timeline(timeline)
        
        # Should be sorted by date
        dates = [item['date'] for item in processed]
        assert dates == sorted(dates)
        
        # Should only contain valid entries
        for item in processed:
            assert item['date']
            assert item['description'].strip()
    
    @given(
        st.lists(portfolio_data(), min_size=0, max_size=20),
        st.text(min_size=0, max_size=50)
    )
    def test_search_filter_matches_title_and_description(self, portfolios, search_query):
        """Search filter should match both title and description"""
        validator = PortfolioValidator()
        
        filters = {'search': search_query}
        filtered = validator.apply_filters(portfolios, filters)
        
        search_lower = search_query.lower().strip()
        
        if not search_lower:
            # Empty search should return all portfolios
            assert len(filtered) == len(portfolios)
        else:
            # All filtered portfolios should match search criteria
            for portfolio in filtered:
                title_match = search_lower in portfolio.get('title', '').lower()
                desc_match = search_lower in portfolio.get('description', '').lower()
                assert title_match or desc_match
    
    @given(st.lists(portfolio_data(), min_size=0, max_size=20))
    def test_featured_filter_consistency(self, portfolios):
        """Featured filter should correctly separate featured and normal portfolios"""
        validator = PortfolioValidator()
        
        # Test featured filter
        featured_filtered = validator.apply_filters(portfolios, {'status': 'featured'})
        assert all(p.get('is_featured', False) for p in featured_filtered)
        
        # Test normal filter
        normal_filtered = validator.apply_filters(portfolios, {'status': 'normal'})
        assert all(not p.get('is_featured', False) for p in normal_filtered)
        
        # Combined should equal original (assuming no other filters)
        total_filtered = len(featured_filtered) + len(normal_filtered)
        assert total_filtered == len(portfolios)
    
    @given(
        st.lists(portfolio_data(), min_size=1, max_size=20),
        st.sampled_from(['title', 'created_at', 'updated_at']),
        st.sampled_from(['asc', 'desc'])
    )
    def test_sorting_maintains_order_consistency(self, portfolios, sort_by, order):
        """Sorting should maintain consistent order for same criteria"""
        validator = PortfolioValidator()
        
        sorted_once = validator.sort_portfolios(portfolios, sort_by, order)
        sorted_twice = validator.sort_portfolios(sorted_once, sort_by, order)
        
        # Should be identical after second sort
        assert sorted_once == sorted_twice
        
        # Should maintain correct order
        if len(sorted_once) > 1:
            for i in range(len(sorted_once) - 1):
                current_val = sorted_once[i].get(sort_by, '')
                next_val = sorted_once[i + 1].get(sort_by, '')
                
                if isinstance(current_val, str):
                    current_val = current_val.lower()
                    next_val = next_val.lower()
                
                if order == 'asc':
                    assert current_val <= next_val
                else:
                    assert current_val >= next_val
    
    @given(st.lists(portfolio_data(), min_size=0, max_size=20))
    def test_crud_operations_maintain_data_integrity(self, portfolios):
        """CRUD operations should maintain data integrity"""
        # Simulate portfolio management operations
        portfolio_list = portfolios.copy()
        
        # Test create operation
        new_portfolio = {
            'id': max([p.get('id', 0) for p in portfolio_list] + [0]) + 1,
            'title': 'New Portfolio',
            'description': 'New portfolio description',
            'content': 'New content',
            'is_featured': False,
            'sort_order': 0,
            'tech_stack': ['Vue.js'],
            'development_timeline': []
        }
        
        portfolio_list.append(new_portfolio)
        assert len(portfolio_list) == len(portfolios) + 1
        assert new_portfolio in portfolio_list
        
        # Test update operation
        if portfolio_list:
            original_count = len(portfolio_list)
            portfolio_to_update = portfolio_list[0].copy()
            portfolio_to_update['title'] = 'Updated Title'
            
            # Replace in list
            portfolio_list[0] = portfolio_to_update
            
            assert len(portfolio_list) == original_count
            assert portfolio_list[0]['title'] == 'Updated Title'
        
        # Test delete operation
        if portfolio_list:
            original_count = len(portfolio_list)
            deleted_portfolio = portfolio_list.pop(0)
            
            assert len(portfolio_list) == original_count - 1
            assert deleted_portfolio not in portfolio_list
    
    @given(
        st.lists(portfolio_data(), min_size=0, max_size=20),
        st.dictionaries(
            st.sampled_from(['search', 'status']),
            st.one_of(
                st.text(min_size=0, max_size=20),
                st.sampled_from(['', 'featured', 'normal'])
            ),
            min_size=0, max_size=2
        )
    )
    def test_filter_combinations_work_correctly(self, portfolios, filters):
        """Multiple filters should work together correctly"""
        validator = PortfolioValidator()
        
        filtered = validator.apply_filters(portfolios, filters)
        
        # Filtered result should be subset of original
        assert len(filtered) <= len(portfolios)
        
        # All filtered items should be in original list
        for item in filtered:
            assert item in portfolios
        
        # Apply filters individually and verify intersection
        if 'search' in filters and 'status' in filters:
            search_filtered = validator.apply_filters(portfolios, {'search': filters['search']})
            status_filtered = validator.apply_filters(portfolios, {'status': filters['status']})
            
            # Combined filter should be intersection
            expected_intersection = [
                p for p in search_filtered if p in status_filtered
            ]
            
            # Should have same length (order might differ)
            assert len(filtered) == len(expected_intersection)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])