"""
联系链接功能性属性测试

属性 8: 联系链接功能性
验证: 需求 4.3

测试联系链接的功能性，包括：
- 邮箱链接格式验证
- 社交媒体链接有效性
- 链接可访问性
- 链接安全性
- 链接打开方式
- 链接跟踪和分析
"""

import pytest
from hypothesis import given, strategies as st, assume, settings
from typing import List, Dict, Any, Optional
import re
from urllib.parse import urlparse


# 联系链接相关的策略
@st.composite
def email_strategy(draw):
    """生成邮箱地址策略"""
    # 生成用户名部分
    username_chars = 'abcdefghijklmnopqrstuvwxyz0123456789.-_'
    username = draw(st.text(alphabet=username_chars, min_size=1, max_size=20))
    username = username.strip('.-_')  # 移除开头和结尾的特殊字符
    
    # 生成域名部分
    domains = ['gmail.com', 'outlook.com', 'yahoo.com', 'company.com', 'example.org']
    domain = draw(st.sampled_from(domains))
    
    return f"{username}@{domain}"


@st.composite
def social_media_url_strategy(draw):
    """生成社交媒体URL策略"""
    platforms = {
        'github': 'https://github.com/',
        'linkedin': 'https://linkedin.com/in/',
        'twitter': 'https://twitter.com/',
        'facebook': 'https://facebook.com/',
        'instagram': 'https://instagram.com/',
        'youtube': 'https://youtube.com/c/',
        'behance': 'https://behance.net/',
        'dribbble': 'https://dribbble.com/'
    }
    
    platform = draw(st.sampled_from(list(platforms.keys())))
    username = draw(st.text(alphabet='abcdefghijklmnopqrstuvwxyz0123456789-_', min_size=1, max_size=30))
    
    return platforms[platform] + username


@st.composite
def contact_info_strategy(draw):
    """生成联系信息策略"""
    return {
        'name': draw(st.text(min_size=1, max_size=50)),
        'title': draw(st.text(min_size=1, max_size=100)),
        'email': draw(email_strategy()),
        'github_url': draw(st.one_of(st.none(), social_media_url_strategy())),
        'linkedin_url': draw(st.one_of(st.none(), social_media_url_strategy())),
        'twitter_url': draw(st.one_of(st.none(), social_media_url_strategy())),
        'website_url': draw(st.one_of(st.none(), st.text(min_size=10, max_size=100))),
        'phone': draw(st.one_of(st.none(), st.text(min_size=10, max_size=20)))
    }


@st.composite
def link_metadata_strategy(draw):
    """生成链接元数据策略"""
    return {
        'url': draw(st.text(min_size=1, max_size=200)),
        'title': draw(st.text(min_size=0, max_size=100)),
        'target': draw(st.sampled_from(['_self', '_blank', '_parent', '_top'])),
        'rel': draw(st.sampled_from(['', 'noopener', 'noreferrer', 'nofollow', 'noopener noreferrer'])),
        'aria_label': draw(st.text(min_size=0, max_size=100)),
        'tracking_enabled': draw(st.booleans()),
        'security_check': draw(st.booleans())
    }


class ContactLinkValidator:
    """联系链接验证器"""
    
    SOCIAL_PLATFORMS = {
        'github.com': {'name': 'GitHub', 'icon': 'github', 'color': '#333'},
        'linkedin.com': {'name': 'LinkedIn', 'icon': 'linkedin', 'color': '#0077b5'},
        'twitter.com': {'name': 'Twitter', 'icon': 'twitter', 'color': '#1da1f2'},
        'facebook.com': {'name': 'Facebook', 'icon': 'facebook', 'color': '#1877f2'},
        'instagram.com': {'name': 'Instagram', 'icon': 'instagram', 'color': '#e4405f'},
        'youtube.com': {'name': 'YouTube', 'icon': 'youtube', 'color': '#ff0000'},
        'behance.net': {'name': 'Behance', 'icon': 'behance', 'color': '#1769ff'},
        'dribbble.com': {'name': 'Dribbble', 'icon': 'dribbble', 'color': '#ea4c89'}
    }
    
    def validate_email(self, email: str) -> Dict[str, Any]:
        """验证邮箱地址"""
        if not email:
            return {'valid': False, 'error': 'Empty email'}
        
        # 基本邮箱格式验证
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(email_pattern, email):
            return {'valid': False, 'error': 'Invalid email format'}
        
        # 检查连续的点号
        if '..' in email:
            return {'valid': False, 'error': 'Consecutive dots not allowed'}
        
        # 检查邮箱长度
        if len(email) > 254:  # RFC 5321 限制
            return {'valid': False, 'error': 'Email too long'}
        
        # 分离用户名和域名
        try:
            username, domain = email.split('@')
            
            # 验证用户名
            if len(username) > 64:  # RFC 5321 限制
                return {'valid': False, 'error': 'Username too long'}
            
            # 检查用户名开头和结尾不能是点号
            if username.startswith('.') or username.endswith('.'):
                return {'valid': False, 'error': 'Username cannot start or end with dot'}
            
            # 验证域名
            if len(domain) > 253:
                return {'valid': False, 'error': 'Domain too long'}
            
            # 检查域名格式
            if domain.startswith('.') or domain.endswith('.') or '..' in domain:
                return {'valid': False, 'error': 'Invalid domain format'}
            
            return {
                'valid': True,
                'username': username,
                'domain': domain,
                'mailto_url': f"mailto:{email}"
            }
        except ValueError:
            return {'valid': False, 'error': 'Invalid email format'}
    
    def validate_social_media_url(self, url: str) -> Dict[str, Any]:
        """验证社交媒体URL"""
        if not url:
            return {'valid': False, 'error': 'Empty URL'}
        
        try:
            parsed = urlparse(url)
            
            if not parsed.scheme or not parsed.netloc:
                return {'valid': False, 'error': 'Invalid URL format'}
            
            # 检查协议
            if parsed.scheme not in ['http', 'https']:
                return {'valid': False, 'error': 'Invalid protocol'}
            
            # 检查是否为已知的社交媒体平台
            domain = parsed.netloc.lower()
            platform_info = None
            
            for platform_domain, info in self.SOCIAL_PLATFORMS.items():
                if platform_domain in domain:
                    platform_info = info
                    break
            
            if not platform_info:
                return {'valid': False, 'error': 'Unknown social media platform'}
            
            # 检查路径是否包含用户名
            if not parsed.path or parsed.path == '/' or parsed.path.endswith('/'):
                return {'valid': False, 'error': 'Missing username in URL'}
            
            # 检查路径长度（去除前缀后应该有用户名）
            path_parts = [part for part in parsed.path.split('/') if part]
            if len(path_parts) == 0:
                return {'valid': False, 'error': 'Missing username in URL'}
            
            return {
                'valid': True,
                'platform': platform_info['name'],
                'domain': domain,
                'path': parsed.path,
                'icon': platform_info['icon'],
                'color': platform_info['color']
            }
        except Exception as e:
            return {'valid': False, 'error': str(e)}
    
    def generate_link_attributes(self, url: str, link_type: str) -> Dict[str, str]:
        """生成链接属性"""
        attributes = {}
        
        # 基本属性
        attributes['href'] = url
        
        # 根据链接类型设置属性
        if link_type == 'email':
            attributes['title'] = '发送邮件'
            attributes['aria-label'] = '发送邮件'
        elif link_type == 'social':
            # 解析社交媒体平台
            validation = self.validate_social_media_url(url)
            if validation['valid']:
                platform = validation['platform']
                attributes['title'] = f'访问我的{platform}主页'
                attributes['aria-label'] = f'访问我的{platform}主页'
                attributes['target'] = '_blank'
                attributes['rel'] = 'noopener noreferrer'
            else:
                # 即使验证失败，也要设置基本的外部链接属性
                attributes['title'] = '访问外部链接'
                attributes['aria-label'] = '访问外部链接'
                attributes['target'] = '_blank'
                attributes['rel'] = 'noopener noreferrer'
        elif link_type == 'external':
            attributes['title'] = '访问外部链接'
            attributes['aria-label'] = '访问外部链接'
            attributes['target'] = '_blank'
            attributes['rel'] = 'noopener noreferrer'
        
        return attributes
    
    def validate_link_security(self, url: str, target: str, rel: str) -> Dict[str, Any]:
        """验证链接安全性"""
        security_issues = []
        
        # 检查外部链接的安全属性
        if target == '_blank':
            if 'noopener' not in rel:
                security_issues.append('Missing noopener for _blank target')
            if 'noreferrer' not in rel:
                security_issues.append('Missing noreferrer for _blank target')
        
        # 检查协议安全性
        try:
            parsed = urlparse(url)
            if parsed.scheme == 'http':
                security_issues.append('Insecure HTTP protocol')
        except:
            security_issues.append('Invalid URL format')
        
        return {
            'secure': len(security_issues) == 0,
            'issues': security_issues
        }
    
    def validate_accessibility(self, link_attrs: Dict[str, str]) -> Dict[str, Any]:
        """验证链接可访问性"""
        accessibility_issues = []
        
        # 检查必要的可访问性属性
        if not link_attrs.get('aria-label') and not link_attrs.get('title'):
            accessibility_issues.append('Missing aria-label or title')
        
        # 检查链接文本
        if not link_attrs.get('text') or len(link_attrs.get('text', '').strip()) == 0:
            if not link_attrs.get('aria-label'):
                accessibility_issues.append('Missing accessible text')
        
        # 检查颜色对比度（简化检查）
        if link_attrs.get('color'):
            # 这里可以添加更复杂的颜色对比度检查
            pass
        
        return {
            'accessible': len(accessibility_issues) == 0,
            'issues': accessibility_issues
        }


# 测试类
class TestContactLinksFunctionality:
    """联系链接功能性测试"""
    
    def setup_method(self):
        """设置测试"""
        self.validator = ContactLinkValidator()
    
    @given(email_strategy())
    @settings(max_examples=50)
    def test_email_validation_accuracy(self, email):
        """测试邮箱验证准确性"""
        result = self.validator.validate_email(email)
        
        # 验证结果应该包含必要字段
        assert 'valid' in result
        
        if result['valid']:
            assert 'username' in result
            assert 'domain' in result
            assert 'mailto_url' in result
            assert result['mailto_url'].startswith('mailto:')
            assert '@' in email
            
            # 验证用户名和域名
            username, domain = email.split('@')
            assert result['username'] == username
            assert result['domain'] == domain
        else:
            assert 'error' in result
            assert isinstance(result['error'], str)
    
    @given(social_media_url_strategy())
    @settings(max_examples=50)
    def test_social_media_url_validation_consistency(self, url):
        """测试社交媒体URL验证一致性"""
        # 同一个URL的验证结果应该一致
        result1 = self.validator.validate_social_media_url(url)
        result2 = self.validator.validate_social_media_url(url)
        
        assert result1 == result2, "Social media URL validation should be consistent"
        
        # 有效的URL应该包含平台信息
        if result1['valid']:
            assert 'platform' in result1
            assert 'domain' in result1
            assert 'icon' in result1
            assert 'color' in result1
            assert result1['platform'] in [info['name'] for info in ContactLinkValidator.SOCIAL_PLATFORMS.values()]
    
    @given(contact_info_strategy())
    @settings(max_examples=30)
    def test_contact_info_validation_completeness(self, contact_info):
        """测试联系信息验证完整性"""
        # 验证邮箱
        email_result = self.validator.validate_email(contact_info['email'])
        assert 'valid' in email_result
        
        # 验证社交媒体链接
        social_links = ['github_url', 'linkedin_url', 'twitter_url']
        for link_key in social_links:
            url = contact_info.get(link_key)
            if url:
                social_result = self.validator.validate_social_media_url(url)
                assert 'valid' in social_result
                
                # 如果验证失败，应该有错误信息
                if not social_result['valid']:
                    assert 'error' in social_result
    
    @given(st.sampled_from(['email', 'social', 'external']), st.text(min_size=10, max_size=100))
    @settings(max_examples=30)
    def test_link_attributes_generation_correctness(self, link_type, url):
        """测试链接属性生成正确性"""
        # 为邮箱链接添加mailto前缀
        if link_type == 'email' and not url.startswith('mailto:'):
            url = f"mailto:{url}"
        
        attributes = self.validator.generate_link_attributes(url, link_type)
        
        # 基本属性检查
        assert 'href' in attributes
        assert attributes['href'] == url
        
        # 根据类型检查特定属性
        if link_type == 'social' or link_type == 'external':
            assert attributes.get('target') == '_blank'
            assert 'noopener' in attributes.get('rel', '')
            assert 'noreferrer' in attributes.get('rel', '')
        
        # 可访问性属性检查
        assert 'title' in attributes or 'aria-label' in attributes
    
    @given(link_metadata_strategy())
    @settings(max_examples=30)
    def test_link_security_validation_thoroughness(self, link_metadata):
        """测试链接安全性验证全面性"""
        url = link_metadata['url']
        target = link_metadata['target']
        rel = link_metadata['rel']
        
        security_result = self.validator.validate_link_security(url, target, rel)
        
        # 验证结果应该包含必要字段
        assert 'secure' in security_result
        assert 'issues' in security_result
        assert isinstance(security_result['issues'], list)
        
        # 如果不安全，应该有具体的问题描述
        if not security_result['secure']:
            assert len(security_result['issues']) > 0
            for issue in security_result['issues']:
                assert isinstance(issue, str)
                assert len(issue) > 0
        
        # 检查特定的安全问题
        if target == '_blank':
            if 'noopener' not in rel:
                assert 'Missing noopener for _blank target' in security_result['issues']
            if 'noreferrer' not in rel:
                assert 'Missing noreferrer for _blank target' in security_result['issues']
    
    @given(link_metadata_strategy())
    @settings(max_examples=30)
    def test_link_accessibility_validation_comprehensiveness(self, link_metadata):
        """测试链接可访问性验证全面性"""
        # 构建链接属性
        link_attrs = {
            'href': link_metadata['url'],
            'title': link_metadata['title'],
            'aria-label': link_metadata['aria_label'],
            'target': link_metadata['target'],
            'rel': link_metadata['rel']
        }
        
        accessibility_result = self.validator.validate_accessibility(link_attrs)
        
        # 验证结果应该包含必要字段
        assert 'accessible' in accessibility_result
        assert 'issues' in accessibility_result
        assert isinstance(accessibility_result['issues'], list)
        
        # 如果不可访问，应该有具体的问题描述
        if not accessibility_result['accessible']:
            assert len(accessibility_result['issues']) > 0
            for issue in accessibility_result['issues']:
                assert isinstance(issue, str)
                assert len(issue) > 0
    
    @given(st.lists(contact_info_strategy(), min_size=1, max_size=5))
    @settings(max_examples=20)
    def test_contact_links_batch_validation_consistency(self, contact_list):
        """测试联系链接批量验证一致性"""
        # 收集所有邮箱和社交媒体链接
        all_emails = []
        all_social_urls = []
        
        for contact in contact_list:
            all_emails.append(contact['email'])
            for key in ['github_url', 'linkedin_url', 'twitter_url']:
                url = contact.get(key)
                if url:
                    all_social_urls.append(url)
        
        # 验证所有邮箱
        email_results = {}
        for email in all_emails:
            email_results[email] = self.validator.validate_email(email)
        
        # 验证所有社交媒体链接
        social_results = {}
        for url in all_social_urls:
            social_results[url] = self.validator.validate_social_media_url(url)
        
        # 相同邮箱的验证结果应该一致
        email_counts = {}
        for email in all_emails:
            email_counts[email] = email_counts.get(email, 0) + 1
        
        for email, count in email_counts.items():
            if count > 1:
                # 重复邮箱的验证结果应该相同
                first_result = email_results[email]
                for other_email in all_emails:
                    if other_email == email:
                        assert email_results[other_email] == first_result
        
        # 相同URL的验证结果应该一致
        url_counts = {}
        for url in all_social_urls:
            url_counts[url] = url_counts.get(url, 0) + 1
        
        for url, count in url_counts.items():
            if count > 1:
                first_result = social_results[url]
                for other_url in all_social_urls:
                    if other_url == url:
                        assert social_results[other_url] == first_result
    
    def test_contact_link_error_scenarios_handling(self):
        """测试联系链接错误场景处理"""
        # 测试各种错误的邮箱格式
        invalid_emails = [
            '',
            'invalid',
            '@domain.com',
            'user@',
            'user@domain',
            'user..name@domain.com',
            'user@domain..com',
            'a' * 65 + '@domain.com',  # 用户名太长
            'user@' + 'a' * 254 + '.com'  # 域名太长
        ]
        
        for email in invalid_emails:
            result = self.validator.validate_email(email)
            assert not result['valid'], f"Email {email} should be invalid"
            assert 'error' in result
        
        # 测试各种错误的URL格式
        invalid_urls = [
            '',
            'not-a-url',
            'http://',
            'https://',
            'ftp://example.com',
            'http://unknown-platform.com/user',
            'https://github.com/',  # 缺少用户名
            'https://linkedin.com/in/',  # 缺少用户名
        ]
        
        for url in invalid_urls:
            result = self.validator.validate_social_media_url(url)
            assert not result['valid'], f"URL {url} should be invalid"
            assert 'error' in result
    
    def test_contact_link_platform_recognition_accuracy(self):
        """测试联系链接平台识别准确性"""
        # 测试各个平台的URL识别
        platform_urls = {
            'GitHub': 'https://github.com/username',
            'LinkedIn': 'https://linkedin.com/in/username',
            'Twitter': 'https://twitter.com/username',
            'Facebook': 'https://facebook.com/username',
            'Instagram': 'https://instagram.com/username',
            'YouTube': 'https://youtube.com/c/username',
            'Behance': 'https://behance.net/username',
            'Dribbble': 'https://dribbble.com/username'
        }
        
        for expected_platform, url in platform_urls.items():
            result = self.validator.validate_social_media_url(url)
            assert result['valid'], f"URL {url} should be valid"
            assert result['platform'] == expected_platform
            assert 'icon' in result
            assert 'color' in result
    
    def test_mailto_link_generation_correctness(self):
        """测试mailto链接生成正确性"""
        test_emails = [
            'user@example.com',
            'test.email@company.org',
            'contact@domain.co.uk'
        ]
        
        for email in test_emails:
            result = self.validator.validate_email(email)
            if result['valid']:
                mailto_url = result['mailto_url']
                assert mailto_url == f"mailto:{email}"
                
                # 生成链接属性
                attributes = self.validator.generate_link_attributes(mailto_url, 'email')
                assert attributes['href'] == mailto_url
                assert 'title' in attributes
                assert 'aria-label' in attributes


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])