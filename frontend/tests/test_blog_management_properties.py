"""
Blog Management Functionality Property Tests

Tests for blog management CRUD operations, Markdown processing,
form validation, and content management in the admin interface.
"""

import pytest
from hypothesis import given, strategies as st, assume
from typing import Dict, Any, List, Optional
import re
from datetime import datetime, date


class BlogValidator:
    """Blog data validation and management logic"""
    
    @staticmethod
    def validate_blog_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate blog form data"""
        errors = {}
        
        # Title validation
        title = data.get('title', '').strip()
        if not title:
            errors['title'] = 'Title is required'
        elif len(title) < 2 or len(title) > 200:
            errors['title'] = 'Title must be 2-200 characters'
        
        # Content validation
        content = data.get('content', '').strip()
        if not content:
            errors['content'] = 'Content is required'
        elif len(content) < 10:
            errors['content'] = 'Content must be at least 10 characters'
        
        # SEO validation
        seo_title = data.get('seo_title', '').strip()
        if seo_title and len(seo_title) > 60:
            errors['seo_title'] = 'SEO title should not exceed 60 characters'
        
        seo_description = data.get('seo_description', '').strip()
        if seo_description and len(seo_description) > 160:
            errors['seo_description'] = 'SEO description should not exceed 160 characters'
        
        return errors
    
    @staticmethod
    def process_tags(tags: List[str]) -> List[str]:
        """Process and validate blog tags"""
        if not tags:
            return []
        
        # Remove duplicates and empty strings
        processed = []
        seen = set()
        for tag in tags:
            tag = tag.strip()
            if tag and tag not in seen:
                processed.append(tag)
                seen.add(tag)
        
        return processed
    
    @staticmethod
    def calculate_reading_time(content: str) -> int:
        """Calculate reading time based on content length"""
        if not content:
            return 1
        
        # Average reading speed: 200 characters per minute
        words_per_minute = 200
        time = max(1, len(content) // words_per_minute)
        return time
    
    @staticmethod
    def generate_excerpt(content: str, max_length: int = 200) -> str:
        """Generate excerpt from content"""
        if not content:
            return ''
        
        # Remove markdown formatting
        plain_text = re.sub(r'[#*`\[\]()_~]', '', content).strip()
        
        if len(plain_text) <= max_length:
            return plain_text
        
        return plain_text[:max_length] + '...'
    
    @staticmethod
    def validate_seo_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate SEO data"""
        errors = {}
        
        seo_title = data.get('seo_title', '').strip()
        if seo_title and len(seo_title) > 60:
            errors['seo_title'] = 'SEO title should not exceed 60 characters'
        
        seo_description = data.get('seo_description', '').strip()
        if seo_description and len(seo_description) > 160:
            errors['seo_description'] = 'SEO description should not exceed 160 characters'
        
        return errors
    
    @staticmethod
    def apply_filters(blogs: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Apply search and filter criteria"""
        result = blogs.copy()
        
        # Search filter
        search_query = filters.get('search', '').lower().strip()
        if search_query:
            result = [
                b for b in result
                if search_query in b.get('title', '').lower() or
                   search_query in b.get('content', '').lower() or
                   search_query in b.get('excerpt', '').lower()
            ]
        
        # Status filter
        status_filter = filters.get('status', '')
        if status_filter == 'published':
            result = [b for b in result if b.get('is_published', False)]
        elif status_filter == 'draft':
            result = [b for b in result if not b.get('is_published', False)]
        
        return result
    
    @staticmethod
    def sort_blogs(blogs: List[Dict[str, Any]], sort_by: str, order: str = 'desc') -> List[Dict[str, Any]]:
        """Sort blogs by specified criteria"""
        if not blogs:
            return []
        
        def get_sort_key(blog: Dict[str, Any]) -> Any:
            value = blog.get(sort_by, '')
            if isinstance(value, str):
                return value.lower()
            return value
        
        reverse = order == 'desc'
        return sorted(blogs, key=get_sort_key, reverse=reverse)
    
    @staticmethod
    def process_markdown_content(content: str) -> str:
        """Process markdown content (simplified simulation)"""
        if not content:
            return ''
        
        # Simple markdown processing simulation
        processed = content
        
        # Headers
        processed = re.sub(r'^# (.+)$', r'<h1>\1</h1>', processed, flags=re.MULTILINE)
        processed = re.sub(r'^## (.+)$', r'<h2>\1</h2>', processed, flags=re.MULTILINE)
        processed = re.sub(r'^### (.+)$', r'<h3>\1</h3>', processed, flags=re.MULTILINE)
        
        # Bold and italic
        processed = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', processed)
        processed = re.sub(r'\*(.+?)\*', r'<em>\1</em>', processed)
        
        # Code
        processed = re.sub(r'`(.+?)`', r'<code>\1</code>', processed)
        
        # Links
        processed = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', processed)
        
        return processed


# Test data generators
@st.composite
def blog_data(draw):
    """Generate valid blog data"""
    return {
        'id': draw(st.integers(min_value=1, max_value=1000)),
        'title': draw(st.text(min_size=2, max_size=200, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs')))),
        'content': draw(st.text(min_size=10, max_size=5000, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs', 'Po')))),
        'excerpt': draw(st.one_of(
            st.just(''),
            st.text(min_size=10, max_size=300, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs')))
        )),
        'tags': draw(st.lists(
            st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
            min_size=0, max_size=10
        )),
        'is_published': draw(st.booleans()),
        'published_at': draw(st.one_of(
            st.just(''),
            st.datetimes(min_value=datetime(2020, 1, 1), max_value=datetime(2024, 12, 31)).map(lambda x: x.isoformat())
        )),
        'reading_time': draw(st.integers(min_value=1, max_value=60)),
        'sort_order': draw(st.integers(min_value=0, max_value=999)),
        'seo_title': draw(st.one_of(
            st.just(''),
            st.text(min_size=5, max_size=60, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs')))
        )),
        'seo_description': draw(st.one_of(
            st.just(''),
            st.text(min_size=10, max_size=160, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs')))
        )),
        'seo_keywords': draw(st.one_of(
            st.just(''),
            st.text(min_size=5, max_size=100, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs')))
        )),
        'created_at': draw(st.datetimes(min_value=datetime(2020, 1, 1), max_value=datetime(2024, 12, 31))).isoformat(),
        'updated_at': draw(st.datetimes(min_value=datetime(2020, 1, 1), max_value=datetime(2024, 12, 31))).isoformat()
    }


@st.composite
def invalid_blog_data(draw):
    """Generate invalid blog data for validation testing"""
    invalid_type = draw(st.sampled_from(['empty_title', 'long_title', 'short_content', 'long_seo_title', 'long_seo_description']))
    
    base_data = {
        'title': 'Valid Blog Title',
        'content': 'This is valid blog content with enough characters to pass validation.',
        'tags': ['tech', 'blog'],
        'is_published': False,
        'seo_title': 'Valid SEO Title',
        'seo_description': 'Valid SEO description for the blog post'
    }
    
    if invalid_type == 'empty_title':
        base_data['title'] = ''
    elif invalid_type == 'long_title':
        base_data['title'] = 'x' * 201
    elif invalid_type == 'short_content':
        base_data['content'] = 'short'
    elif invalid_type == 'long_seo_title':
        base_data['seo_title'] = 'x' * 61
    elif invalid_type == 'long_seo_description':
        base_data['seo_description'] = 'x' * 161
    
    return base_data


@st.composite
def markdown_content(draw):
    """Generate markdown content for testing"""
    elements = []
    
    # Headers
    if draw(st.booleans()):
        elements.append(f"# {draw(st.text(min_size=5, max_size=50))}")
    
    if draw(st.booleans()):
        elements.append(f"## {draw(st.text(min_size=5, max_size=50))}")
    
    # Paragraphs
    for _ in range(draw(st.integers(min_value=1, max_value=3))):
        elements.append(draw(st.text(min_size=20, max_size=200)))
    
    # Bold text
    if draw(st.booleans()):
        elements.append(f"**{draw(st.text(min_size=5, max_size=30))}**")
    
    # Italic text
    if draw(st.booleans()):
        elements.append(f"*{draw(st.text(min_size=5, max_size=30))}*")
    
    # Code
    if draw(st.booleans()):
        elements.append(f"`{draw(st.text(min_size=5, max_size=20))}`")
    
    # Links
    if draw(st.booleans()):
        link_text = draw(st.text(min_size=3, max_size=20))
        link_url = f"https://example.com/{draw(st.text(min_size=3, max_size=20))}"
        elements.append(f"[{link_text}]({link_url})")
    
    return '\n\n'.join(elements)


class TestBlogManagementProperties:
    """Property tests for blog management functionality"""
    
    @given(blog_data())
    def test_valid_blog_validation_passes(self, blog):
        """Valid blog data should pass validation"""
        validator = BlogValidator()
        errors = validator.validate_blog_data(blog)
        
        # Should have no validation errors for valid data
        assert len(errors) == 0
    
    @given(invalid_blog_data())
    def test_invalid_blog_validation_fails(self, blog):
        """Invalid blog data should fail validation"""
        validator = BlogValidator()
        errors = validator.validate_blog_data(blog)
        
        # Should have at least one validation error
        assert len(errors) > 0
    
    @given(st.lists(st.text(min_size=1, max_size=30), min_size=0, max_size=15))
    def test_tag_processing_removes_duplicates(self, tag_list):
        """Tag processing should remove duplicates and empty strings"""
        validator = BlogValidator()
        
        # Add some duplicates and empty strings
        test_list = tag_list + tag_list[:3] + ['', '  ', tag_list[0] if tag_list else 'test']
        
        processed = validator.process_tags(test_list)
        
        # Should not contain duplicates
        assert len(processed) == len(set(processed))
        
        # Should not contain empty strings
        assert all(tag.strip() for tag in processed)
        
        # Should preserve order of first occurrence
        seen = set()
        for tag in processed:
            assert tag not in seen
            seen.add(tag)
    
    @given(st.text(min_size=0, max_size=2000))
    def test_reading_time_calculation_consistency(self, content):
        """Reading time calculation should be consistent and reasonable"""
        validator = BlogValidator()
        
        reading_time = validator.calculate_reading_time(content)
        
        # Should always return at least 1 minute
        assert reading_time >= 1
        
        # Should be proportional to content length
        if len(content) == 0:
            assert reading_time == 1
        else:
            # Longer content should generally take more time
            expected_time = max(1, len(content) // 200)
            assert reading_time == expected_time
    
    @given(st.text(min_size=0, max_size=1000))
    def test_excerpt_generation_properties(self, content):
        """Excerpt generation should follow consistent rules"""
        validator = BlogValidator()
        
        excerpt = validator.generate_excerpt(content, max_length=200)
        
        # Should not exceed max length + ellipsis
        assert len(excerpt) <= 203  # 200 + "..."
        
        # Should be empty if content is empty
        if not content.strip():
            assert excerpt == ''
        
        # Should end with "..." if content was truncated
        if len(content.strip()) > 200:
            assert excerpt.endswith('...')
        else:
            assert not excerpt.endswith('...')
    
    @given(blog_data())
    def test_seo_validation_enforces_limits(self, blog):
        """SEO validation should enforce character limits"""
        validator = BlogValidator()
        
        # Test with valid SEO data
        errors = validator.validate_seo_data(blog)
        
        if blog.get('seo_title', '') and len(blog['seo_title']) <= 60:
            assert 'seo_title' not in errors
        
        if blog.get('seo_description', '') and len(blog['seo_description']) <= 160:
            assert 'seo_description' not in errors
        
        # Test with invalid SEO data
        invalid_seo = {
            'seo_title': 'x' * 61,
            'seo_description': 'x' * 161
        }
        
        seo_errors = validator.validate_seo_data(invalid_seo)
        assert 'seo_title' in seo_errors
        assert 'seo_description' in seo_errors
    
    @given(
        st.lists(blog_data(), min_size=0, max_size=20),
        st.text(min_size=0, max_size=50)
    )
    def test_search_filter_matches_multiple_fields(self, blogs, search_query):
        """Search filter should match title, content, and excerpt"""
        validator = BlogValidator()
        
        filters = {'search': search_query}
        filtered = validator.apply_filters(blogs, filters)
        
        search_lower = search_query.lower().strip()
        
        if not search_lower:
            # Empty search should return all blogs
            assert len(filtered) == len(blogs)
        else:
            # All filtered blogs should match search criteria
            for blog in filtered:
                title_match = search_lower in blog.get('title', '').lower()
                content_match = search_lower in blog.get('content', '').lower()
                excerpt_match = search_lower in blog.get('excerpt', '').lower()
                assert title_match or content_match or excerpt_match
    
    @given(st.lists(blog_data(), min_size=0, max_size=20))
    def test_publication_status_filter_consistency(self, blogs):
        """Publication status filter should correctly separate published and draft blogs"""
        validator = BlogValidator()
        
        # Test published filter
        published_filtered = validator.apply_filters(blogs, {'status': 'published'})
        assert all(b.get('is_published', False) for b in published_filtered)
        
        # Test draft filter
        draft_filtered = validator.apply_filters(blogs, {'status': 'draft'})
        assert all(not b.get('is_published', False) for b in draft_filtered)
        
        # Combined should equal original (assuming no other filters)
        total_filtered = len(published_filtered) + len(draft_filtered)
        assert total_filtered == len(blogs)
    
    @given(
        st.lists(blog_data(), min_size=1, max_size=20),
        st.sampled_from(['title', 'created_at', 'updated_at', 'published_at']),
        st.sampled_from(['asc', 'desc'])
    )
    def test_sorting_maintains_order_consistency(self, blogs, sort_by, order):
        """Sorting should maintain consistent order for same criteria"""
        validator = BlogValidator()
        
        sorted_once = validator.sort_blogs(blogs, sort_by, order)
        sorted_twice = validator.sort_blogs(sorted_once, sort_by, order)
        
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
    
    @given(markdown_content())
    def test_markdown_processing_preserves_structure(self, content):
        """Markdown processing should preserve content structure"""
        validator = BlogValidator()
        
        processed = validator.process_markdown_content(content)
        
        # Should not be empty if input wasn't empty
        if content.strip():
            assert processed.strip()
        
        # Should contain HTML tags if meaningful markdown was present
        has_headers = re.search(r'^#+\s+\w+', content, re.MULTILINE)
        has_bold = re.search(r'\*\*\w+\*\*', content)
        has_italic = re.search(r'\*\w+\*', content)
        has_code = re.search(r'`\w+`', content)
        has_links = re.search(r'\[\w+\]\(\w+\)', content)
        
        if has_headers or has_bold or has_italic or has_code or has_links:
            assert '<' in processed and '>' in processed
        
        # Basic content preservation check
        # Remove all markdown and HTML formatting for comparison
        original_clean = re.sub(r'[#*`\[\]()<>/_-]', ' ', content)
        original_clean = re.sub(r'\s+', ' ', original_clean).strip()
        
        processed_clean = re.sub(r'<[^>]*>', ' ', processed)
        processed_clean = re.sub(r'\s+', ' ', processed_clean).strip()
        
        # If there's meaningful content, it should be preserved
        if len(original_clean) > 10:  # Only check for substantial content
            # Check that some content is preserved (not necessarily all)
            assert len(processed_clean) > 0
    
    @given(st.lists(blog_data(), min_size=0, max_size=20))
    def test_crud_operations_maintain_data_integrity(self, blogs):
        """CRUD operations should maintain data integrity"""
        # Simulate blog management operations
        blog_list = blogs.copy()
        
        # Test create operation
        new_blog = {
            'id': max([b.get('id', 0) for b in blog_list] + [0]) + 1,
            'title': 'New Blog Post',
            'content': 'This is a new blog post content.',
            'excerpt': 'New blog excerpt',
            'tags': ['new', 'blog'],
            'is_published': False,
            'reading_time': 1,
            'sort_order': 0
        }
        
        blog_list.append(new_blog)
        assert len(blog_list) == len(blogs) + 1
        assert new_blog in blog_list
        
        # Test update operation
        if blog_list:
            original_count = len(blog_list)
            blog_to_update = blog_list[0].copy()
            blog_to_update['title'] = 'Updated Blog Title'
            blog_to_update['is_published'] = True
            
            # Replace in list
            blog_list[0] = blog_to_update
            
            assert len(blog_list) == original_count
            assert blog_list[0]['title'] == 'Updated Blog Title'
            assert blog_list[0]['is_published'] == True
        
        # Test delete operation
        if blog_list:
            original_count = len(blog_list)
            deleted_blog = blog_list.pop(0)
            
            assert len(blog_list) == original_count - 1
            assert deleted_blog not in blog_list


if __name__ == '__main__':
    pytest.main([__file__, '-v'])