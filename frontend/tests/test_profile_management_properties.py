"""
Profile Management Functionality Property Tests

Tests for profile management functionality, rich text editing,
avatar upload, skill management, and contact information validation.
"""

import pytest
from hypothesis import given, strategies as st, assume
from typing import Dict, Any, List, Optional
import re
from datetime import datetime


class ProfileValidator:
    """Profile data validation and management logic"""
    
    @staticmethod
    def validate_profile_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate profile form data"""
        errors = {}
        
        # Name validation
        name = data.get('name', '').strip()
        if not name:
            errors['name'] = 'Name is required'
        elif len(name) < 2 or len(name) > 50:
            errors['name'] = 'Name must be 2-50 characters'
        
        # Title validation
        title = data.get('title', '').strip()
        if not title:
            errors['title'] = 'Title is required'
        elif len(title) < 2 or len(title) > 100:
            errors['title'] = 'Title must be 2-100 characters'
        
        # Bio validation
        bio = data.get('bio', '').strip()
        if not bio:
            errors['bio'] = 'Bio is required'
        
        # Email validation
        email = data.get('email', '').strip()
        if email and not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
            errors['email'] = 'Invalid email format'
        
        # Phone validation
        phone = data.get('phone', '').strip()
        if phone and not re.match(r'^[\+]?[0-9\s\-\(\)]{8,20}$', phone):
            errors['phone'] = 'Invalid phone format'
        
        # URL validations
        github_url = data.get('github_url', '').strip()
        if github_url and not re.match(r'^https?://(www\.)?github\.com/.+', github_url):
            errors['github_url'] = 'Invalid GitHub URL'
        
        linkedin_url = data.get('linkedin_url', '').strip()
        if linkedin_url and not re.match(r'^https?://(www\.)?linkedin\.com/.+', linkedin_url):
            errors['linkedin_url'] = 'Invalid LinkedIn URL'
        
        twitter_url = data.get('twitter_url', '').strip()
        if twitter_url and not re.match(r'^https?://(www\.)?twitter\.com/.+', twitter_url):
            errors['twitter_url'] = 'Invalid Twitter URL'
        
        website_url = data.get('website_url', '').strip()
        if website_url and not re.match(r'^https?://.+', website_url):
            errors['website_url'] = 'Invalid website URL'
        
        return errors
    
    @staticmethod
    def validate_skill_data(skill: Dict[str, Any]) -> Dict[str, Any]:
        """Validate individual skill data"""
        errors = {}
        
        name = skill.get('name', '').strip()
        if not name:
            errors['name'] = 'Skill name is required'
        elif len(name) > 50:
            errors['name'] = 'Skill name too long'
        
        category = skill.get('category', '').strip()
        valid_categories = ['frontend', 'backend', 'mobile', 'database', 'cloud', 'tools', 'design', 'other']
        if not category or category not in valid_categories:
            errors['category'] = 'Invalid skill category'
        
        level = skill.get('level', 0)
        if not isinstance(level, (int, float)) or level < 0 or level > 100:
            errors['level'] = 'Skill level must be 0-100'
        
        description = skill.get('description', '')
        if description and len(description) > 200:
            errors['description'] = 'Description too long'
        
        return errors
    
    @staticmethod
    def process_skills(skills: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process and validate skills list"""
        if not skills:
            return []
        
        processed = []
        seen_names = set()
        
        for skill in skills:
            # Skip invalid skills
            if not skill.get('name', '').strip():
                continue
            
            name = skill['name'].strip()
            
            # Remove duplicates
            if name in seen_names:
                continue
            
            seen_names.add(name)
            
            # Normalize data
            processed_skill = {
                'name': name,
                'category': skill.get('category', 'other'),
                'level': max(0, min(100, int(skill.get('level', 0)))),
                'description': skill.get('description', '').strip()
            }
            
            processed.append(processed_skill)
        
        return processed
    
    @staticmethod
    def calculate_skill_stats(skills: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate skill statistics"""
        if not skills:
            return {
                'total_skills': 0,
                'average_level': 0,
                'categories': 0,
                'expert_skills': 0,
                'by_category': {}
            }
        
        total_skills = len(skills)
        total_level = sum(skill['level'] for skill in skills)
        average_level = total_level / total_skills if total_skills > 0 else 0
        expert_skills = len([s for s in skills if s['level'] >= 80])
        
        # Group by category
        by_category = {}
        for skill in skills:
            category = skill['category']
            if category not in by_category:
                by_category[category] = {
                    'count': 0,
                    'total_level': 0,
                    'skills': []
                }
            
            by_category[category]['count'] += 1
            by_category[category]['total_level'] += skill['level']
            by_category[category]['skills'].append(skill['name'])
        
        # Calculate average level per category
        for category_data in by_category.values():
            category_data['average_level'] = category_data['total_level'] / category_data['count']
        
        return {
            'total_skills': total_skills,
            'average_level': round(average_level, 1),
            'categories': len(by_category),
            'expert_skills': expert_skills,
            'by_category': by_category
        }
    
    @staticmethod
    def sanitize_rich_text(content: str) -> str:
        """Sanitize rich text content"""
        if not content:
            return ''
        
        # Remove potentially dangerous tags and attributes
        dangerous_tags = ['script', 'iframe', 'object', 'embed', 'form', 'input']
        dangerous_attrs = ['onclick', 'onload', 'onerror', 'javascript:']
        
        sanitized = content
        
        # Remove dangerous tags
        for tag in dangerous_tags:
            sanitized = re.sub(f'<{tag}[^>]*>.*?</{tag}>', '', sanitized, flags=re.IGNORECASE | re.DOTALL)
            sanitized = re.sub(f'<{tag}[^>]*/?>', '', sanitized, flags=re.IGNORECASE)
        
        # Remove dangerous attributes
        for attr in dangerous_attrs:
            sanitized = re.sub(f'{attr}[^>]*', '', sanitized, flags=re.IGNORECASE)
        
        return sanitized.strip()
    
    @staticmethod
    def validate_avatar_file(file_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate avatar file data"""
        errors = {}
        
        file_type = str(file_data.get('type', ''))
        if not file_type.startswith('image/'):
            errors['type'] = 'File must be an image'
        
        file_size = file_data.get('size', 0)
        try:
            file_size = int(file_size)
            max_size = 2 * 1024 * 1024  # 2MB
            if file_size > max_size:
                errors['size'] = 'File size exceeds 2MB limit'
        except (ValueError, TypeError):
            errors['size'] = 'Invalid file size'
        
        return errors


# Test data generators
@st.composite
def profile_data(draw):
    """Generate valid profile data"""
    return {
        'id': draw(st.integers(min_value=1, max_value=1000)),
        'name': draw(st.text(min_size=2, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Zs'))).filter(lambda x: len(x.strip()) >= 2)),
        'title': draw(st.text(min_size=2, max_size=100, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs'))).filter(lambda x: len(x.strip()) >= 2)),
        'bio': draw(st.text(min_size=10, max_size=1000, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs', 'Po'))).filter(lambda x: len(x.strip()) >= 10)),
        'avatar_url': draw(st.one_of(
            st.just(''),
            st.text(min_size=10, max_size=200).map(lambda x: f'https://example.com/avatars/{x}.jpg')
        )),
        'email': draw(st.one_of(
            st.just(''),
            st.text(min_size=5, max_size=30, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))).map(
                lambda x: f'{x}@example.com'
            )
        )),
        'phone': draw(st.one_of(
            st.just(''),
            st.text(min_size=8, max_size=15, alphabet='0123456789-()').map(lambda x: '+' + x if x else x),
            st.text(min_size=8, max_size=15, alphabet='0123456789')
        )),
        'location': draw(st.one_of(
            st.just(''),
            st.text(min_size=5, max_size=100, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Zs')))
        )),
        'github_url': draw(st.one_of(
            st.just(''),
            st.text(min_size=5, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))).map(
                lambda x: f'https://github.com/{x}'
            )
        )),
        'linkedin_url': draw(st.one_of(
            st.just(''),
            st.text(min_size=5, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))).map(
                lambda x: f'https://linkedin.com/in/{x}'
            )
        )),
        'twitter_url': draw(st.one_of(
            st.just(''),
            st.text(min_size=5, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))).map(
                lambda x: f'https://twitter.com/{x}'
            )
        )),
        'website_url': draw(st.one_of(
            st.just(''),
            st.text(min_size=5, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))).map(
                lambda x: f'https://{x}.com'
            )
        )),
        'skills': draw(st.lists(
            st.fixed_dictionaries({
                'name': st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs'))),
                'category': st.sampled_from(['frontend', 'backend', 'mobile', 'database', 'cloud', 'tools', 'design', 'other']),
                'level': st.integers(min_value=0, max_value=100),
                'description': st.text(min_size=0, max_size=200, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs', 'Po')))
            }),
            min_size=0, max_size=20
        )),
        'created_at': draw(st.datetimes(min_value=datetime(2020, 1, 1), max_value=datetime(2024, 12, 31))).isoformat(),
        'updated_at': draw(st.datetimes(min_value=datetime(2020, 1, 1), max_value=datetime(2024, 12, 31))).isoformat()
    }


@st.composite
def invalid_profile_data(draw):
    """Generate invalid profile data for validation testing"""
    invalid_type = draw(st.sampled_from(['empty_name', 'long_name', 'empty_title', 'invalid_email', 'invalid_github']))
    
    base_data = {
        'name': 'Valid Name',
        'title': 'Valid Title',
        'bio': 'Valid bio content',
        'email': 'valid@example.com',
        'github_url': 'https://github.com/user',
        'skills': []
    }
    
    if invalid_type == 'empty_name':
        base_data['name'] = ''
    elif invalid_type == 'long_name':
        base_data['name'] = 'x' * 51
    elif invalid_type == 'empty_title':
        base_data['title'] = ''
    elif invalid_type == 'invalid_email':
        base_data['email'] = 'invalid-email'
    elif invalid_type == 'invalid_github':
        base_data['github_url'] = 'https://example.com/not-github'
    
    return base_data


@st.composite
def skill_data(draw):
    """Generate skill data"""
    return {
        'name': draw(st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs')))),
        'category': draw(st.sampled_from(['frontend', 'backend', 'mobile', 'database', 'cloud', 'tools', 'design', 'other'])),
        'level': draw(st.integers(min_value=0, max_value=100)),
        'description': draw(st.text(min_size=0, max_size=200))
    }


@st.composite
def rich_text_content(draw):
    """Generate rich text content"""
    elements = []
    
    # Basic text
    elements.append(draw(st.text(min_size=10, max_size=200)))
    
    # Bold text
    if draw(st.booleans()):
        elements.append(f"<strong>{draw(st.text(min_size=5, max_size=50))}</strong>")
    
    # Italic text
    if draw(st.booleans()):
        elements.append(f"<em>{draw(st.text(min_size=5, max_size=50))}</em>")
    
    # Links
    if draw(st.booleans()):
        link_text = draw(st.text(min_size=3, max_size=30))
        link_url = f"https://example.com/{draw(st.text(min_size=3, max_size=20))}"
        elements.append(f'<a href="{link_url}">{link_text}</a>')
    
    # Lists
    if draw(st.booleans()):
        list_items = [f"<li>{draw(st.text(min_size=5, max_size=30))}</li>" for _ in range(draw(st.integers(min_value=1, max_value=5)))]
        elements.append(f"<ul>{''.join(list_items)}</ul>")
    
    return ' '.join(elements)


class TestProfileManagementProperties:
    """Property tests for profile management functionality"""
    
    @given(profile_data())
    def test_valid_profile_validation_passes(self, profile):
        """Valid profile data should pass validation"""
        validator = ProfileValidator()
        errors = validator.validate_profile_data(profile)
        
        # Should have no validation errors for valid data
        assert len(errors) == 0
    
    @given(invalid_profile_data())
    def test_invalid_profile_validation_fails(self, profile):
        """Invalid profile data should fail validation"""
        validator = ProfileValidator()
        errors = validator.validate_profile_data(profile)
        
        # Should have at least one validation error
        assert len(errors) > 0
    
    @given(skill_data())
    def test_valid_skill_validation_passes(self, skill):
        """Valid skill data should pass validation"""
        validator = ProfileValidator()
        errors = validator.validate_skill_data(skill)
        
        # Should have no validation errors for valid data
        assert len(errors) == 0
    
    @given(st.lists(skill_data(), min_size=0, max_size=20))
    def test_skill_processing_removes_duplicates(self, skills):
        """Skill processing should remove duplicates and invalid entries"""
        validator = ProfileValidator()
        
        # Add some duplicates and invalid entries
        test_skills = skills + skills[:3] + [{'name': '', 'category': 'frontend', 'level': 50}]
        
        processed = validator.process_skills(test_skills)
        
        # Should not contain duplicates
        names = [skill['name'] for skill in processed]
        assert len(names) == len(set(names))
        
        # Should not contain empty names
        assert all(skill['name'].strip() for skill in processed)
        
        # Should normalize levels
        for skill in processed:
            assert 0 <= skill['level'] <= 100
    
    @given(st.lists(skill_data(), min_size=0, max_size=15))
    def test_skill_statistics_calculation(self, skills):
        """Skill statistics should be calculated correctly"""
        validator = ProfileValidator()
        
        processed_skills = validator.process_skills(skills)
        stats = validator.calculate_skill_stats(processed_skills)
        
        # Basic statistics validation
        assert stats['total_skills'] == len(processed_skills)
        
        if processed_skills:
            expected_avg = sum(skill['level'] for skill in processed_skills) / len(processed_skills)
            assert abs(stats['average_level'] - expected_avg) < 0.1
            
            expected_experts = len([s for s in processed_skills if s['level'] >= 80])
            assert stats['expert_skills'] == expected_experts
            
            # Category statistics
            categories = set(skill['category'] for skill in processed_skills)
            assert stats['categories'] == len(categories)
            
            # Each category should have correct counts
            for category, data in stats['by_category'].items():
                category_skills = [s for s in processed_skills if s['category'] == category]
                assert data['count'] == len(category_skills)
                
                if category_skills:
                    expected_avg = sum(s['level'] for s in category_skills) / len(category_skills)
                    assert abs(data['average_level'] - expected_avg) < 0.1
        else:
            assert stats['average_level'] == 0
            assert stats['expert_skills'] == 0
            assert stats['categories'] == 0
    
    @given(rich_text_content())
    def test_rich_text_sanitization(self, content):
        """Rich text sanitization should remove dangerous content"""
        validator = ProfileValidator()
        
        # Add some dangerous content
        dangerous_content = content + '<script>alert("xss")</script><iframe src="evil.com"></iframe>'
        
        sanitized = validator.sanitize_rich_text(dangerous_content)
        
        # Should not contain dangerous tags
        assert '<script>' not in sanitized.lower()
        assert '<iframe>' not in sanitized.lower()
        assert 'javascript:' not in sanitized.lower()
        assert 'onclick' not in sanitized.lower()
        
        # Should preserve safe content
        if content.strip():
            # Some of the original content should be preserved
            assert len(sanitized) > 0
    
    @given(
        st.dictionaries(
            st.sampled_from(['type', 'size']),
            st.one_of(
                st.text(min_size=1, max_size=20),
                st.integers(min_value=0, max_value=10 * 1024 * 1024)
            ),
            min_size=1, max_size=2
        )
    )
    def test_avatar_file_validation(self, file_data):
        """Avatar file validation should enforce type and size limits"""
        validator = ProfileValidator()
        
        errors = validator.validate_avatar_file(file_data)
        
        # Check type validation
        if 'type' in file_data:
            file_type = file_data['type']
            if not str(file_type).startswith('image/'):
                assert 'type' in errors
            else:
                assert 'type' not in errors
        
        # Check size validation
        if 'size' in file_data:
            file_size = file_data['size']
            if isinstance(file_size, int) and file_size > 2 * 1024 * 1024:
                assert 'size' in errors
            elif isinstance(file_size, int) and file_size <= 2 * 1024 * 1024:
                assert 'size' not in errors
    
    @given(profile_data())
    def test_profile_data_consistency(self, profile):
        """Profile data should maintain consistency across operations"""
        validator = ProfileValidator()
        
        # Validate original data
        original_errors = validator.validate_profile_data(profile)
        
        # Process skills
        processed_skills = validator.process_skills(profile['skills'])
        
        # Create updated profile with processed skills
        updated_profile = {**profile, 'skills': processed_skills}
        updated_errors = validator.validate_profile_data(updated_profile)
        
        # Validation results should be consistent
        # (processed skills might fix some issues, so updated should have <= errors)
        skill_related_errors = ['skills']  # Add any skill-related error keys
        
        non_skill_errors_original = {k: v for k, v in original_errors.items() if k not in skill_related_errors}
        non_skill_errors_updated = {k: v for k, v in updated_errors.items() if k not in skill_related_errors}
        
        # Non-skill errors should remain the same
        assert non_skill_errors_original == non_skill_errors_updated
    
    @given(st.lists(profile_data(), min_size=0, max_size=10))
    def test_profile_crud_operations_integrity(self, profiles):
        """Profile CRUD operations should maintain data integrity"""
        # Simulate profile management operations
        profile_list = profiles.copy()
        
        # Test create operation
        new_profile = {
            'id': max([p.get('id', 0) for p in profile_list] + [0]) + 1,
            'name': 'New User',
            'title': 'New Title',
            'bio': 'New bio content',
            'skills': [],
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        profile_list.append(new_profile)
        assert len(profile_list) == len(profiles) + 1
        assert new_profile in profile_list
        
        # Test update operation
        if profile_list:
            original_count = len(profile_list)
            profile_to_update = profile_list[0].copy()
            profile_to_update['name'] = 'Updated Name'
            profile_to_update['updated_at'] = datetime.now().isoformat()
            
            # Replace in list
            profile_list[0] = profile_to_update
            
            assert len(profile_list) == original_count
            assert profile_list[0]['name'] == 'Updated Name'
        
        # Test delete operation
        if profile_list:
            original_count = len(profile_list)
            deleted_profile = profile_list.pop(0)
            
            assert len(profile_list) == original_count - 1
            assert deleted_profile not in profile_list


if __name__ == '__main__':
    pytest.main([__file__, '-v'])