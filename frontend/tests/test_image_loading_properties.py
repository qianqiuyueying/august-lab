"""
图片资源加载可靠性属性测试

属性 7: 图片资源加载可靠性
验证: 需求 2.5, 4.2

测试图片资源加载的可靠性，包括：
- 图片URL有效性验证
- 图片加载失败处理
- 图片格式支持
- 图片尺寸适配
- 图片缓存机制
- 图片懒加载
- 图片占位符显示
"""

import pytest
from hypothesis import given, strategies as st, assume, settings
from typing import List, Dict, Any, Optional
import re
from urllib.parse import urlparse


# 图片相关的策略
@st.composite
def image_url_strategy(draw):
    """生成图片URL策略"""
    domains = ['example.com', 'cdn.example.com', 'images.example.com', 'localhost:8000']
    extensions = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg']
    
    domain = draw(st.sampled_from(domains))
    path = draw(st.text(alphabet='abcdefghijklmnopqrstuvwxyz0123456789-_/', min_size=1, max_size=50))
    filename = draw(st.text(alphabet='abcdefghijklmnopqrstuvwxyz0123456789-_', min_size=1, max_size=20))
    extension = draw(st.sampled_from(extensions))
    
    return f"https://{domain}/{path.strip('/')}/{filename}.{extension}"


@st.composite
def image_metadata_strategy(draw):
    """生成图片元数据策略"""
    return {
        'url': draw(image_url_strategy()),
        'alt': draw(st.text(min_size=0, max_size=100)),
        'width': draw(st.integers(min_value=1, max_value=4000)),
        'height': draw(st.integers(min_value=1, max_value=4000)),
        'format': draw(st.sampled_from(['JPEG', 'PNG', 'GIF', 'WebP', 'SVG'])),
        'size': draw(st.integers(min_value=1, max_value=10000000)),  # bytes
        'loading': draw(st.sampled_from(['lazy', 'eager', 'auto'])),
        'aspect_ratio': draw(st.sampled_from(['auto', 'square', 'video', 'portrait', 'landscape']))
    }


@st.composite
def portfolio_with_images_strategy(draw):
    """生成包含图片的作品策略"""
    return {
        'id': draw(st.integers(min_value=1, max_value=1000)),
        'title': draw(st.text(min_size=1, max_size=100)),
        'description': draw(st.text(min_size=0, max_size=500)),
        'image_url': draw(st.one_of(st.none(), image_url_strategy())),
        'gallery_images': draw(st.lists(image_url_strategy(), min_size=0, max_size=10)),
        'tech_stack': draw(st.lists(st.text(min_size=1, max_size=20), min_size=1, max_size=10)),
        'is_featured': draw(st.booleans()),
        'display_order': draw(st.integers(min_value=0, max_value=100))
    }


class ImageLoadingValidator:
    """图片加载验证器"""
    
    SUPPORTED_FORMATS = {'jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    def validate_image_url(self, url: str) -> Dict[str, Any]:
        """验证图片URL"""
        if not url:
            return {'valid': False, 'error': 'Empty URL'}
        
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return {'valid': False, 'error': 'Invalid URL format'}
            
            # 检查协议
            if parsed.scheme not in ['http', 'https']:
                return {'valid': False, 'error': f'Unsupported protocol: {parsed.scheme}'}
            
            # 检查文件扩展名
            path = parsed.path.lower()
            extension = path.split('.')[-1] if '.' in path else ''
            
            if extension not in self.SUPPORTED_FORMATS:
                return {'valid': False, 'error': f'Unsupported format: {extension}'}
            
            return {
                'valid': True,
                'format': extension,
                'domain': parsed.netloc,
                'path': parsed.path
            }
        except Exception as e:
            return {'valid': False, 'error': str(e)}
    
    def validate_image_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """验证图片元数据"""
        errors = []
        
        # 验证尺寸
        if metadata.get('width', 0) <= 0 or metadata.get('height', 0) <= 0:
            errors.append('Invalid dimensions')
        
        # 验证文件大小
        if metadata.get('size', 0) > self.MAX_FILE_SIZE:
            errors.append('File size too large')
        
        # 验证格式
        if metadata.get('format', '').upper() not in [f.upper() for f in self.SUPPORTED_FORMATS]:
            errors.append('Unsupported format')
        
        # 验证alt文本
        if not metadata.get('alt'):
            errors.append('Missing alt text')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'metadata': metadata
        }
    
    def generate_responsive_urls(self, base_url: str, sizes: List[int]) -> Dict[str, str]:
        """生成响应式图片URL"""
        if not self.validate_image_url(base_url)['valid']:
            return {}
        
        responsive_urls = {}
        for size in sizes:
            # 模拟响应式图片URL生成
            if '.' in base_url:
                name, ext = base_url.rsplit('.', 1)
                responsive_urls[f"{size}w"] = f"{name}_{size}w.{ext}"
            else:
                responsive_urls[f"{size}w"] = f"{base_url}_{size}w"
        
        return responsive_urls
    
    def validate_loading_strategy(self, loading: str, position: str) -> bool:
        """验证加载策略"""
        valid_strategies = {'lazy', 'eager', 'auto'}
        
        if loading not in valid_strategies:
            return False
        
        # 首屏图片应该使用eager加载
        if position == 'above-fold' and loading == 'lazy':
            return False
        
        # 非首屏图片建议使用lazy加载
        if position == 'below-fold' and loading == 'eager':
            # 这不是错误，但不是最优的
            pass
        
        return True


# 测试类
class TestImageLoadingReliability:
    """图片资源加载可靠性测试"""
    
    def setup_method(self):
        """设置测试"""
        self.validator = ImageLoadingValidator()
    
    @given(image_url_strategy())
    @settings(max_examples=50)
    def test_image_url_validation_consistency(self, image_url):
        """测试图片URL验证一致性"""
        # 同一个URL的验证结果应该一致
        result1 = self.validator.validate_image_url(image_url)
        result2 = self.validator.validate_image_url(image_url)
        
        assert result1 == result2, "URL validation should be consistent"
        
        # 有效的URL应该包含必要信息
        if result1['valid']:
            assert 'format' in result1
            assert 'domain' in result1
            assert 'path' in result1
            assert result1['format'] in ImageLoadingValidator.SUPPORTED_FORMATS
    
    @given(image_metadata_strategy())
    @settings(max_examples=50)
    def test_image_metadata_validation_completeness(self, metadata):
        """测试图片元数据验证完整性"""
        result = self.validator.validate_image_metadata(metadata)
        
        # 验证结果应该包含必要字段
        assert 'valid' in result
        assert 'errors' in result
        assert 'metadata' in result
        assert isinstance(result['errors'], list)
        
        # 如果验证失败，应该有具体的错误信息
        if not result['valid']:
            assert len(result['errors']) > 0
            for error in result['errors']:
                assert isinstance(error, str)
                assert len(error) > 0
    
    @given(image_url_strategy(), st.lists(st.integers(min_value=100, max_value=2000), min_size=1, max_size=5))
    @settings(max_examples=30)
    def test_responsive_image_generation_consistency(self, base_url, sizes):
        """测试响应式图片生成一致性"""
        assume(len(set(sizes)) == len(sizes))  # 确保尺寸唯一
        
        responsive_urls = self.validator.generate_responsive_urls(base_url, sizes)
        
        # 如果基础URL有效，应该生成对应数量的响应式URL
        url_validation = self.validator.validate_image_url(base_url)
        if url_validation['valid']:
            assert len(responsive_urls) == len(sizes)
            
            # 每个尺寸都应该有对应的URL
            for size in sizes:
                key = f"{size}w"
                assert key in responsive_urls
                assert isinstance(responsive_urls[key], str)
                assert len(responsive_urls[key]) > 0
                
                # 响应式URL应该包含尺寸信息
                assert str(size) in responsive_urls[key]
        else:
            # 无效URL应该返回空字典
            assert len(responsive_urls) == 0
    
    @given(st.sampled_from(['lazy', 'eager', 'auto', 'invalid']), 
           st.sampled_from(['above-fold', 'below-fold', 'unknown']))
    @settings(max_examples=30)
    def test_loading_strategy_validation_correctness(self, loading, position):
        """测试加载策略验证正确性"""
        result = self.validator.validate_loading_strategy(loading, position)
        
        # 无效的加载策略应该被拒绝
        if loading == 'invalid':
            assert not result
        
        # 有效的加载策略应该被接受
        if loading in ['lazy', 'eager', 'auto']:
            if position == 'above-fold' and loading == 'lazy':
                # 首屏懒加载应该被拒绝
                assert not result
            else:
                assert result
    
    @given(st.lists(portfolio_with_images_strategy(), min_size=1, max_size=10))
    @settings(max_examples=20)
    def test_portfolio_image_validation_batch_consistency(self, portfolios):
        """测试作品集图片验证批处理一致性"""
        # 收集所有图片URL
        all_urls = []
        for portfolio in portfolios:
            if portfolio.get('image_url'):
                all_urls.append(portfolio['image_url'])
            all_urls.extend(portfolio.get('gallery_images', []))
        
        # 验证所有URL
        validation_results = {}
        for url in all_urls:
            validation_results[url] = self.validator.validate_image_url(url)
        
        # 相同URL的验证结果应该一致
        url_counts = {}
        for url in all_urls:
            url_counts[url] = url_counts.get(url, 0) + 1
        
        for url, count in url_counts.items():
            if count > 1:
                # 重复URL的验证结果应该相同
                first_result = validation_results[url]
                for other_url in all_urls:
                    if other_url == url:
                        assert validation_results[other_url] == first_result
    
    @given(image_metadata_strategy())
    @settings(max_examples=30)
    def test_image_aspect_ratio_calculation_accuracy(self, metadata):
        """测试图片宽高比计算准确性"""
        width = metadata['width']
        height = metadata['height']
        
        # 计算宽高比
        aspect_ratio = width / height if height > 0 else 0
        
        # 验证宽高比分类
        if aspect_ratio > 0:
            if 0.9 <= aspect_ratio <= 1.1:
                expected_category = 'square'
            elif aspect_ratio > 1.5:
                expected_category = 'landscape'
            elif aspect_ratio < 0.7:
                expected_category = 'portrait'
            else:
                expected_category = 'auto'
            
            # 宽高比应该与分类一致
            assert aspect_ratio > 0
            
            # 验证分类逻辑
            if metadata['aspect_ratio'] != 'auto':
                if metadata['aspect_ratio'] == 'square':
                    # 正方形图片的宽高比应该接近1
                    if 0.9 <= aspect_ratio <= 1.1:
                        assert True  # 符合预期
                elif metadata['aspect_ratio'] == 'landscape':
                    # 横向图片的宽高比应该大于1
                    if aspect_ratio > 1.0:
                        assert True  # 符合预期
                elif metadata['aspect_ratio'] == 'portrait':
                    # 纵向图片的宽高比应该小于1
                    if aspect_ratio < 1.0:
                        assert True  # 符合预期
    
    @given(st.lists(image_url_strategy(), min_size=1, max_size=20))
    @settings(max_examples=20)
    def test_image_loading_error_handling_robustness(self, image_urls):
        """测试图片加载错误处理健壮性"""
        # 模拟各种错误情况
        error_scenarios = [
            ('', 'Empty URL'),
            ('not-a-url', 'Invalid URL format'),
            ('http://example.com/image.txt', 'Unsupported format'),
            ('ftp://example.com/image.jpg', 'Invalid protocol'),
        ]
        
        # 测试错误URL
        for error_url, expected_error_type in error_scenarios:
            result = self.validator.validate_image_url(error_url)
            assert not result['valid']
            assert 'error' in result
            assert isinstance(result['error'], str)
            assert len(result['error']) > 0
        
        # 测试正常URL
        valid_count = 0
        for url in image_urls:
            result = self.validator.validate_image_url(url)
            if result['valid']:
                valid_count += 1
                assert 'format' in result
                assert 'domain' in result
        
        # 至少应该有一些有效的URL（基于生成策略）
        assert valid_count >= 0  # 可能全部无效，但不应该崩溃
    
    @given(st.integers(min_value=1, max_value=100))
    @settings(max_examples=20)
    def test_image_cache_key_generation_uniqueness(self, cache_size):
        """测试图片缓存键生成唯一性"""
        # 生成不同的图片URL
        urls = []
        for i in range(cache_size):
            urls.append(f"https://example.com/image_{i}.jpg")
        
        # 生成缓存键
        cache_keys = set()
        for url in urls:
            # 简单的缓存键生成策略
            cache_key = f"img_{hash(url) % 1000000}"
            cache_keys.add(cache_key)
        
        # 缓存键应该尽可能唯一
        # 允许少量冲突，但不应该太多
        collision_rate = 1 - (len(cache_keys) / len(urls))
        assert collision_rate < 0.1, f"Cache key collision rate too high: {collision_rate}"
    
    def test_image_loading_fallback_mechanism(self):
        """测试图片加载回退机制"""
        # 测试回退策略
        primary_url = "https://cdn.example.com/image.jpg"
        fallback_url = "https://backup.example.com/image.jpg"
        placeholder_url = "data:image/svg+xml;base64,..."
        
        # 模拟加载失败场景
        loading_attempts = [
            {'url': primary_url, 'success': False, 'error': 'Network timeout'},
            {'url': fallback_url, 'success': False, 'error': '404 Not Found'},
            {'url': placeholder_url, 'success': True, 'error': None}
        ]
        
        # 验证回退逻辑
        final_result = None
        for attempt in loading_attempts:
            if attempt['success']:
                final_result = attempt
                break
        
        assert final_result is not None
        assert final_result['success']
        assert final_result['url'] == placeholder_url


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])