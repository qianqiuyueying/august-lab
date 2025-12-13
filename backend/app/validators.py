"""
自定义验证器和验证工具
"""

import re
from typing import Optional
from urllib.parse import urlparse

def validate_url(url: Optional[str]) -> Optional[str]:
    """验证URL格式"""
    if not url:
        return None
    
    url = url.strip()
    if not url:
        return None
    
    # 如果不包含协议，添加https://
    if not url.startswith(('http://', 'https://')):
        url = f'https://{url}'
    
    try:
        result = urlparse(url)
        if not all([result.scheme, result.netloc]):
            raise ValueError('无效的URL格式')
        return url
    except Exception:
        raise ValueError('无效的URL格式')

def validate_github_url(url: Optional[str]) -> Optional[str]:
    """验证GitHub URL"""
    if not url:
        return None
    
    url = validate_url(url)
    if url and 'github.com' not in url.lower():
        raise ValueError('必须是有效的GitHub链接')
    
    return url

def validate_linkedin_url(url: Optional[str]) -> Optional[str]:
    """验证LinkedIn URL"""
    if not url:
        return None
    
    url = validate_url(url)
    if url and 'linkedin.com' not in url.lower():
        raise ValueError('必须是有效的LinkedIn链接')
    
    return url

def validate_twitter_url(url: Optional[str]) -> Optional[str]:
    """验证Twitter URL"""
    if not url:
        return None
    
    url = validate_url(url)
    if url and not any(domain in url.lower() for domain in ['twitter.com', 'x.com']):
        raise ValueError('必须是有效的Twitter/X链接')
    
    return url

def sanitize_html(text: str) -> str:
    """清理HTML标签（简单实现）"""
    if not text:
        return text
    
    # 移除常见的HTML标签
    html_pattern = re.compile(r'<[^>]+>')
    return html_pattern.sub('', text)

def validate_markdown_content(content: str) -> str:
    """验证Markdown内容"""
    if not content or not content.strip():
        raise ValueError('内容不能为空')
    
    # 检查内容长度
    if len(content) > 100000:  # 100KB限制
        raise ValueError('内容过长，请控制在100KB以内')
    
    return content.strip()

def validate_tech_stack_item(tech: str) -> str:
    """验证技术栈项目"""
    if not tech or not tech.strip():
        raise ValueError('技术栈项目不能为空')
    
    tech = tech.strip()
    
    # 检查长度
    if len(tech) > 50:
        raise ValueError('技术栈项目名称过长')
    
    # 检查是否包含特殊字符
    if re.search(r'[<>"\']', tech):
        raise ValueError('技术栈项目名称包含无效字符')
    
    return tech

def validate_tag(tag: str) -> str:
    """验证标签"""
    if not tag or not tag.strip():
        raise ValueError('标签不能为空')
    
    tag = tag.strip()
    
    # 检查长度
    if len(tag) > 30:
        raise ValueError('标签名称过长')
    
    # 检查是否包含特殊字符
    if re.search(r'[<>"\',]', tag):
        raise ValueError('标签名称包含无效字符')
    
    return tag

def validate_display_order(order: int) -> int:
    """验证显示顺序"""
    if order < 0:
        raise ValueError('显示顺序不能为负数')
    
    if order > 9999:
        raise ValueError('显示顺序不能超过9999')
    
    return order

def validate_skill_level(level: int) -> int:
    """验证技能熟练度"""
    if level < 0:
        raise ValueError('技能熟练度不能为负数')
    
    if level > 100:
        raise ValueError('技能熟练度不能超过100')
    
    return level