"""
最终集成属性测试
验证产品错误隔离性和整体系统集成
"""

import pytest
from hypothesis import given, strategies as st, assume, settings
import tempfile
import zipfile
import os
from pathlib import Path
from typing import Dict, List
import json
import time

from app.services.product_file_service import ProductFileService
from app.services.product_extension_service import product_extension_service
from app.models import Product as ProductModel


class TestFinalIntegrationProperties:
    """最终集成属性测试"""
    
    def setup_method(self):
        """测试设置"""
        self.file_service = ProductFileService("test_products")
        # 确保扩展已加载
        product_extension_service.load_extensions_from_directory()
        
        # 如果扩展目录中的扩展没有加载成功，使用内置扩展
        if not product_extension_service.registry.get_product_type_extension('static'):
            from app.services.product_extension_service import register_builtin_extensions
            register_builtin_extensions()
    
    def teardown_method(self):
        """测试清理"""
        # 清理测试文件
        import shutil
        if Path("test_products").exists():
            shutil.rmtree("test_products")
    
    @given(
        error_content=st.text(min_size=10, max_size=1000),
        product_count=st.integers(min_value=2, max_value=5)
    )
    @settings(max_examples=20)
    def test_product_error_isolation(self, error_content: str, product_count: int):
        """
        Feature: product-integration, Property 7: 产品错误隔离性
        验证产品应用错误不影响主网站或其他产品的正常运行
        """
        # 获取可用的产品类型
        available_types = product_extension_service.get_available_product_types()
        assume(len(available_types) > 0)
        
        # 创建多个产品
        products = []
        for i in range(product_count):
            import random
            product_type_def = random.choice(available_types)
            product_type = product_type_def['type_name']
            
            type_extension = product_extension_service.registry.get_product_type_extension(product_type)
            assume(type_extension is not None)
            
            # 生成产品文件
            files = self._generate_product_files_with_error(product_type, error_content, i)
            
            # 验证文件处理不会影响其他产品
            try:
                processed_files = type_extension.process_product_files(files)
                
                # 验证处理后的文件仍然包含原始文件
                for original_file in files:
                    assert original_file in processed_files, f"产品 {i} 的文件 {original_file} 在处理后丢失"
                
                # 验证错误隔离 - 一个产品的错误不应该影响文件处理
                assert len(processed_files) >= len(files), f"产品 {i} 的文件处理结果不完整"
                
                products.append({
                    'id': i,
                    'type': product_type,
                    'files': processed_files,
                    'extension': type_extension
                })
                
            except Exception as e:
                # 即使一个产品处理失败，也不应该影响其他产品
                # 这里我们记录错误但继续处理其他产品
                print(f"产品 {i} 处理失败: {str(e)}")
        
        # 验证至少有一些产品成功处理
        assert len(products) > 0, "所有产品都处理失败，可能存在系统性问题"
        
        # 验证每个成功的产品都是独立的
        for product in products:
            # 验证产品配置独立性
            launch_config = product['extension'].get_launch_config({})
            assert isinstance(launch_config, dict), f"产品 {product['id']} 的启动配置无效"
            
            # 验证沙箱权限设置
            if 'sandbox_permissions' in launch_config:
                permissions = launch_config['sandbox_permissions']
                assert isinstance(permissions, list), f"产品 {product['id']} 的沙箱权限配置无效"
                assert 'allow-scripts' in permissions, f"产品 {product['id']} 缺少基本脚本权限"
    
    @given(
        concurrent_operations=st.integers(min_value=2, max_value=4),
        operation_delay=st.floats(min_value=0.01, max_value=0.1)
    )
    @settings(max_examples=10)
    def test_concurrent_product_operations(self, concurrent_operations: int, operation_delay: float):
        """
        验证并发产品操作的隔离性和一致性
        """
        # 获取可用的产品类型
        available_types = product_extension_service.get_available_product_types()
        assume(len(available_types) > 0)
        
        import threading
        import random
        
        results = []
        errors = []
        
        def process_product(product_id: int):
            try:
                # 随机选择产品类型
                product_type_def = random.choice(available_types)
                product_type = product_type_def['type_name']
                
                type_extension = product_extension_service.registry.get_product_type_extension(product_type)
                if not type_extension:
                    errors.append(f"产品 {product_id}: 扩展不存在")
                    return
                
                # 生成测试文件
                files = self._generate_basic_product_files(product_type)
                
                # 模拟处理延迟
                time.sleep(operation_delay)
                
                # 处理文件
                processed_files = type_extension.process_product_files(files)
                
                # 验证处理结果
                if len(processed_files) >= len(files):
                    results.append({
                        'product_id': product_id,
                        'product_type': product_type,
                        'original_files': len(files),
                        'processed_files': len(processed_files),
                        'success': True
                    })
                else:
                    errors.append(f"产品 {product_id}: 文件处理不完整")
                    
            except Exception as e:
                errors.append(f"产品 {product_id}: {str(e)}")
        
        # 创建并启动多个线程
        threads = []
        for i in range(concurrent_operations):
            thread = threading.Thread(target=process_product, args=(i,))
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join(timeout=5.0)  # 5秒超时
        
        # 验证结果
        successful_operations = len(results)
        total_operations = concurrent_operations
        
        # 至少应该有一半的操作成功
        assert successful_operations >= total_operations // 2, \
            f"并发操作成功率过低: {successful_operations}/{total_operations}, 错误: {errors}"
        
        # 验证每个成功的操作都是独立的
        product_ids = [r['product_id'] for r in results]
        assert len(set(product_ids)) == len(product_ids), "产品ID不唯一，可能存在并发冲突"
    
    @given(
        malicious_content=st.text(min_size=50, max_size=500),
        file_count=st.integers(min_value=1, max_value=5)
    )
    @settings(max_examples=15)
    def test_security_isolation_properties(self, malicious_content: str, file_count: int):
        """
        验证产品安全隔离属性
        """
        # 获取可用的产品类型
        available_types = product_extension_service.get_available_product_types()
        assume(len(available_types) > 0)
        
        import random
        product_type_def = random.choice(available_types)
        product_type = product_type_def['type_name']
        
        type_extension = product_extension_service.registry.get_product_type_extension(product_type)
        assume(type_extension is not None)
        
        # 生成包含潜在恶意内容的文件
        files = {}
        
        # 添加基本的有效文件
        if product_type == 'static':
            files['index.html'] = self._generate_html_with_content(malicious_content).encode('utf-8')
        elif product_type == 'spa':
            files['index.html'] = self._generate_spa_html().encode('utf-8')
            files['app.js'] = f"// {malicious_content}\nconsole.log('SPA App');".encode('utf-8')
        
        # 添加额外的测试文件
        for i in range(file_count - 1):
            filename = f"test_{i}.js"
            content = f"// Test file {i}\n// Content: {malicious_content[:100]}\nconsole.log('test');"
            files[filename] = content.encode('utf-8')
        
        # 验证文件
        is_valid, error_msg = type_extension.validate_product_files(files)
        
        if is_valid:
            # 如果文件通过验证，处理文件
            processed_files = type_extension.process_product_files(files)
            
            # 验证处理后的文件安全性
            assert len(processed_files) >= len(files), "文件处理后数量减少"
            
            # 验证增强脚本被添加
            enhancement_files = [f for f in processed_files.keys() if f.startswith('_')]
            assert len(enhancement_files) > 0, "缺少安全增强脚本"
            
            # 验证启动配置包含安全设置
            launch_config = type_extension.get_launch_config({})
            
            if 'sandbox_permissions' in launch_config:
                permissions = launch_config['sandbox_permissions']
                # 验证基本的安全权限设置
                assert 'allow-scripts' in permissions, "缺少脚本执行权限"
                assert 'allow-same-origin' in permissions, "缺少同源权限"
                
                # 验证没有危险权限
                dangerous_permissions = ['allow-top-navigation', 'allow-popups-to-escape-sandbox']
                for perm in dangerous_permissions:
                    if perm in permissions:
                        # 这可能是合理的，但需要记录
                        print(f"警告: 产品类型 {product_type} 包含潜在危险权限: {perm}")
        else:
            # 如果文件验证失败，这是预期的安全行为
            assert error_msg is not None and len(error_msg) > 0, "验证失败但没有错误消息"
    
    @given(
        system_load=st.integers(min_value=1, max_value=10),
        memory_limit=st.sampled_from(['64MB', '128MB', '256MB', '512MB'])
    )
    @settings(max_examples=10)
    def test_system_resource_isolation(self, system_load: int, memory_limit: str):
        """
        验证系统资源隔离和限制
        """
        # 获取可用的产品类型
        available_types = product_extension_service.get_available_product_types()
        assume(len(available_types) > 0)
        
        import random
        
        # 模拟系统负载
        products_processed = 0
        total_memory_allocated = 0
        
        for i in range(system_load):
            product_type_def = random.choice(available_types)
            product_type = product_type_def['type_name']
            
            type_extension = product_extension_service.registry.get_product_type_extension(product_type)
            if not type_extension:
                continue
            
            # 生成产品配置，包含内存限制
            product_config = {
                'performance': {
                    'max_memory': memory_limit
                }
            }
            
            # 获取启动配置
            launch_config = type_extension.get_launch_config(product_config)
            
            # 验证内存限制设置
            if 'memory_limit' in launch_config:
                config_memory = launch_config['memory_limit']
                assert config_memory.endswith(('MB', 'GB')), f"内存限制格式无效: {config_memory}"
                
                # 解析内存大小
                if config_memory.endswith('MB'):
                    memory_mb = int(config_memory[:-2])
                elif config_memory.endswith('GB'):
                    memory_mb = int(config_memory[:-2]) * 1024
                
                total_memory_allocated += memory_mb
                products_processed += 1
        
        # 验证资源分配合理性
        if products_processed > 0:
            average_memory = total_memory_allocated / products_processed
            assert average_memory > 0, "平均内存分配为零"
            assert average_memory <= 1024, f"平均内存分配过高: {average_memory}MB"
            
            # 验证总内存使用不会过度
            max_reasonable_total = system_load * 512  # 每个产品最多512MB
            assert total_memory_allocated <= max_reasonable_total, \
                f"总内存分配过高: {total_memory_allocated}MB > {max_reasonable_total}MB"
    
    def _generate_product_files_with_error(self, product_type: str, error_content: str, product_id: int) -> Dict[str, bytes]:
        """生成包含错误内容的产品文件"""
        files = {}
        
        if product_type == 'static':
            html_content = f'''<!DOCTYPE html>
<html>
<head>
    <title>Test Product {product_id}</title>
</head>
<body>
    <h1>Product {product_id}</h1>
    <script>
    // Error content: {error_content[:100]}
    try {{
        console.log('Product {product_id} loaded');
    }} catch (e) {{
        console.error('Error in product {product_id}:', e);
    }}
    </script>
</body>
</html>'''
            files['index.html'] = html_content.encode('utf-8')
            
        elif product_type == 'spa':
            html_content = f'''<!DOCTYPE html>
<html>
<head>
    <title>SPA Product {product_id}</title>
</head>
<body>
    <div id="root"></div>
    <script>
    // Error content: {error_content[:100]}
    console.log('SPA Product {product_id}');
    </script>
</body>
</html>'''
            files['index.html'] = html_content.encode('utf-8')
        
        # 添加CSS文件
        css_content = f'''/* Product {product_id} styles */
body {{
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 20px;
}}
/* Error content: {error_content[:50]} */
'''
        files['style.css'] = css_content.encode('utf-8')
        
        return files
    
    def _generate_basic_product_files(self, product_type: str) -> Dict[str, bytes]:
        """生成基本的产品文件"""
        files = {}
        
        if product_type == 'static':
            files['index.html'] = b'''<!DOCTYPE html>
<html>
<head><title>Test</title></head>
<body><h1>Test</h1></body>
</html>'''
        elif product_type == 'spa':
            files['index.html'] = b'''<!DOCTYPE html>
<html>
<head><title>SPA Test</title></head>
<body><div id="root"></div></body>
</html>'''
        
        files['style.css'] = b'body { margin: 0; }'
        files['script.js'] = b'console.log("test");'
        
        return files
    
    def _generate_html_with_content(self, content: str) -> str:
        """生成包含指定内容的HTML"""
        return f'''<!DOCTYPE html>
<html>
<head>
    <title>Test HTML</title>
</head>
<body>
    <h1>Test Content</h1>
    <div>
        <!-- Content: {content[:200]} -->
    </div>
    <script>
    console.log('HTML loaded');
    </script>
</body>
</html>'''
    
    def _generate_spa_html(self) -> str:
        """生成SPA HTML内容"""
        return '''<!DOCTYPE html>
<html>
<head>
    <title>SPA Test</title>
</head>
<body>
    <div id="root"></div>
    <script>
    console.log('SPA loaded');
    </script>
</body>
</html>'''


# 运行测试的辅助函数
if __name__ == "__main__":
    pytest.main([__file__, "-v"])