"""
产品类型支持属性测试
验证不同产品类型的支持完整性
"""

import pytest
from hypothesis import given, strategies as st, assume, settings
import tempfile
import zipfile
import os
from pathlib import Path
from typing import Dict, List
import json

from app.services.product_file_service import ProductFileService
from app.services.product_extension_service import product_extension_service
from app.models import Product as ProductModel


class TestProductTypeSupportProperties:
    """产品类型支持属性测试"""
    
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
        title=st.text(min_size=1, max_size=100),
        description=st.text(max_size=500)
    )
    @settings(max_examples=50)
    def test_product_type_support_completeness(self, title: str, description: str):
        """
        Feature: product-integration, Property 5: 产品类型支持完整性
        验证不同产品类型的支持
        """
        # 获取所有可用的产品类型
        available_types = product_extension_service.get_available_product_types()
        assume(len(available_types) > 0)
        
        # 随机选择一个可用的产品类型
        import random
        product_type_def = random.choice(available_types)
        product_type = product_type_def['type_name']
        
        # 获取产品类型扩展
        type_extension = product_extension_service.registry.get_product_type_extension(product_type)
        
        # 验证扩展存在
        assert type_extension is not None, f"产品类型 {product_type} 的扩展不存在"
        
        # 验证扩展元数据
        metadata = type_extension.get_metadata()
        assert metadata.name is not None
        assert metadata.version is not None
        assert metadata.description is not None
        
        # 验证产品类型定义
        type_def = type_extension.get_product_type_definition()
        assert type_def.type_name == product_type
        assert type_def.display_name is not None
        assert type_def.description is not None
        assert len(type_def.file_extensions) > 0
        assert len(type_def.entry_files) > 0
        assert type_def.config_schema is not None
    
    def test_product_type_file_validation(self):
        """
        验证产品类型的文件验证功能
        """
        # 获取所有可用的产品类型
        available_types = product_extension_service.get_available_product_types()
        assume(len(available_types) > 0)
        
        # 随机选择一个可用的产品类型
        import random
        product_type_def = random.choice(available_types)
        product_type = product_type_def['type_name']
        
        type_extension = product_extension_service.registry.get_product_type_extension(product_type)
        assume(type_extension is not None)
        
        type_def = type_extension.get_product_type_definition()
        
        # 测试有效文件集合
        valid_files = self._generate_valid_files_for_type(product_type, type_def)
        is_valid, error_msg = type_extension.validate_product_files(valid_files)
        
        assert is_valid, f"有效文件验证失败: {error_msg}"
        
        # 测试无效文件集合（缺少入口文件）
        invalid_files = {f"test.{ext.lstrip('.')}" for ext in type_def.file_extensions[:3]}
        invalid_files = {name: b"test content" for name in invalid_files}
        
        is_valid, error_msg = type_extension.validate_product_files(invalid_files)
        assert not is_valid, "应该拒绝缺少入口文件的文件集合"
        assert error_msg is not None and len(error_msg) > 0
    
    def test_product_type_file_processing(self):
        """
        验证产品类型的文件处理功能
        """
        # 获取所有可用的产品类型
        available_types = product_extension_service.get_available_product_types()
        assume(len(available_types) > 0)
        
        # 随机选择一个可用的产品类型
        import random
        product_type_def = random.choice(available_types)
        product_type = product_type_def['type_name']
        
        type_extension = product_extension_service.registry.get_product_type_extension(product_type)
        assume(type_extension is not None)
        
        type_def = type_extension.get_product_type_definition()
        
        # 生成测试文件
        original_files = self._generate_valid_files_for_type(product_type, type_def)
        
        # 处理文件
        processed_files = type_extension.process_product_files(original_files)
        
        # 验证处理结果
        assert isinstance(processed_files, dict)
        assert len(processed_files) >= len(original_files)  # 可能添加了增强文件
        
        # 验证原始文件仍然存在
        for filename in original_files:
            assert filename in processed_files, f"原始文件 {filename} 在处理后丢失"
    
    @given(
        config_data=st.dictionaries(
            st.text(min_size=1, max_size=20),
            st.one_of(st.text(), st.integers(), st.booleans()),
            min_size=0,
            max_size=5
        )
    )
    @settings(max_examples=30)
    def test_product_type_launch_config(self, config_data: Dict):
        """
        验证产品类型的启动配置功能
        """
        # 获取所有可用的产品类型
        available_types = product_extension_service.get_available_product_types()
        assume(len(available_types) > 0)
        
        # 随机选择一个可用的产品类型
        import random
        product_type_def = random.choice(available_types)
        product_type = product_type_def['type_name']
        
        type_extension = product_extension_service.registry.get_product_type_extension(product_type)
        assume(type_extension is not None)
        
        # 获取启动配置
        launch_config = type_extension.get_launch_config(config_data)
        
        # 验证启动配置结构
        assert isinstance(launch_config, dict)
        
        # 验证必要的配置项
        if "sandbox_permissions" in launch_config:
            assert isinstance(launch_config["sandbox_permissions"], list)
            assert all(isinstance(perm, str) for perm in launch_config["sandbox_permissions"])
        
        if "memory_limit" in launch_config:
            assert isinstance(launch_config["memory_limit"], str)
            assert launch_config["memory_limit"].endswith(("MB", "GB"))
    
    @given(
        files_count=st.integers(min_value=1, max_value=10),
        file_size=st.integers(min_value=100, max_value=10000)
    )
    @settings(max_examples=20)
    def test_static_web_validation_properties(self, files_count: int, file_size: int):
        """
        验证静态Web应用的特定验证属性
        """
        type_extension = product_extension_service.registry.get_product_type_extension('static')
        assume(type_extension is not None)
        
        # 生成HTML文件
        html_content = self._generate_valid_html_content()
        files = {"index.html": html_content.encode('utf-8')}
        
        # 添加其他文件
        for i in range(files_count - 1):
            filename = f"file_{i}.css" if i % 2 == 0 else f"script_{i}.js"
            content = "/* test content */" if filename.endswith('.css') else "// test content"
            files[filename] = (content * (file_size // len(content))).encode('utf-8')
        
        # 验证文件
        is_valid, error_msg = type_extension.validate_product_files(files)
        
        if file_size * files_count < 100 * 1024 * 1024:  # 小于100MB
            assert is_valid, f"静态Web应用验证失败: {error_msg}"
        # 如果文件太大，可能会失败，这是预期的
    
    @given(
        has_package_json=st.booleans(),
        framework=st.sampled_from(['react', 'vue', 'angular', 'svelte'])
    )
    @settings(max_examples=20)
    def test_spa_framework_detection(self, has_package_json: bool, framework: str):
        """
        验证SPA框架检测功能
        """
        type_extension = product_extension_service.registry.get_product_type_extension('spa')
        assume(type_extension is not None)
        
        files = {"index.html": self._generate_spa_html_content().encode('utf-8')}
        
        if has_package_json:
            # 添加package.json
            package_data = {
                "name": "test-app",
                "version": "1.0.0",
                "dependencies": {
                    framework: "^1.0.0"
                }
            }
            files["package.json"] = json.dumps(package_data).encode('utf-8')
        
        # 添加框架特定文件
        if framework == 'react':
            files["App.jsx"] = b"import React from 'react';"
        elif framework == 'vue':
            files["App.vue"] = b"<template><div>Vue App</div></template>"
        elif framework == 'angular':
            files["app.component.ts"] = b"@Component({}) export class AppComponent {}"
        
        # 验证文件
        is_valid, error_msg = type_extension.validate_product_files(files)
        assert is_valid, f"SPA应用验证失败: {error_msg}"
    
    @given(
        has_canvas=st.booleans(),
        has_webgl=st.booleans(),
        has_wasm=st.booleans()
    )
    @settings(max_examples=20)
    def test_game_type_validation(self, has_canvas: bool, has_webgl: bool, has_wasm: bool):
        """
        验证游戏类型的特定验证
        """
        type_extension = product_extension_service.registry.get_product_type_extension('game')
        assume(type_extension is not None)
        
        # 生成游戏HTML内容
        html_content = self._generate_game_html_content(has_canvas, has_webgl)
        files = {"index.html": html_content.encode('utf-8')}
        
        if has_wasm:
            # 添加WebAssembly文件（模拟WASM文件头）
            wasm_content = b'\x00asm\x01\x00\x00\x00'  # WASM文件头
            files["game.wasm"] = wasm_content
        
        # 验证文件
        is_valid, error_msg = type_extension.validate_product_files(files)
        
        if has_canvas or has_webgl:
            assert is_valid, f"游戏应用验证失败: {error_msg}"
        else:
            # 如果没有Canvas或WebGL，可能会失败
            pass
    
    @given(
        tool_type=st.sampled_from(['calculator', 'editor', 'converter']),
        has_interactive_elements=st.booleans()
    )
    @settings(max_examples=20)
    def test_tool_type_validation(self, tool_type: str, has_interactive_elements: bool):
        """
        验证工具类型的特定验证
        """
        type_extension = product_extension_service.registry.get_product_type_extension('tool')
        assume(type_extension is not None)
        
        # 生成工具HTML内容
        html_content = self._generate_tool_html_content(tool_type, has_interactive_elements)
        files = {"index.html": html_content.encode('utf-8')}
        
        # 验证文件
        is_valid, error_msg = type_extension.validate_product_files(files)
        
        if has_interactive_elements:
            assert is_valid, f"工具应用验证失败: {error_msg}"
        else:
            # 如果没有交互元素，可能会失败
            pass
    
    def _generate_valid_files_for_type(self, product_type: str, type_def) -> Dict[str, bytes]:
        """为指定产品类型生成有效的文件集合"""
        files = {}
        
        # 添加入口文件
        entry_file = type_def.entry_files[0]
        
        if product_type == 'static':
            files[entry_file] = self._generate_valid_html_content().encode('utf-8')
        elif product_type == 'spa':
            files[entry_file] = self._generate_spa_html_content().encode('utf-8')
        elif product_type == 'game':
            files[entry_file] = self._generate_game_html_content(True, True).encode('utf-8')
        elif product_type == 'tool':
            files[entry_file] = self._generate_tool_html_content('calculator', True).encode('utf-8')
        
        # 添加一些通用文件
        files["style.css"] = b"body { margin: 0; }"
        files["script.js"] = b"console.log('Hello World');"
        
        return files
    
    def _generate_valid_html_content(self) -> str:
        """生成有效的HTML内容"""
        return '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>测试静态网站</title>
</head>
<body>
    <div id="app">
        <h1>静态网站测试</h1>
        <p>这是一个测试页面</p>
    </div>
</body>
</html>'''
    
    def _generate_spa_html_content(self) -> str:
        """生成SPA HTML内容"""
        return '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SPA测试应用</title>
</head>
<body>
    <div id="root"></div>
    <script src="bundle.js"></script>
</body>
</html>'''
    
    def _generate_game_html_content(self, has_canvas: bool, has_webgl: bool) -> str:
        """生成游戏HTML内容"""
        canvas_tag = '<canvas id="gameCanvas" width="800" height="600"></canvas>' if has_canvas else ''
        webgl_script = '''
        <script>
        const canvas = document.getElementById('gameCanvas');
        const gl = canvas.getContext('webgl');
        if (gl) {
            console.log('WebGL initialized');
        }
        </script>
        ''' if has_webgl else ''
        
        return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>游戏测试</title>
</head>
<body>
    <div id="gameContainer">
        <h1>游戏测试</h1>
        {canvas_tag}
    </div>
    {webgl_script}
</body>
</html>'''
    
    def _generate_tool_html_content(self, tool_type: str, has_interactive: bool) -> str:
        """生成工具HTML内容"""
        interactive_elements = ''
        if has_interactive:
            if tool_type == 'calculator':
                interactive_elements = '''
                <input type="number" id="num1" placeholder="数字1">
                <input type="number" id="num2" placeholder="数字2">
                <button onclick="calculate()">计算</button>
                <div id="result"></div>
                '''
            elif tool_type == 'editor':
                interactive_elements = '''
                <textarea id="editor" rows="10" cols="50" placeholder="在此输入文本"></textarea>
                <button onclick="save()">保存</button>
                '''
            elif tool_type == 'converter':
                interactive_elements = '''
                <select id="fromUnit">
                    <option value="m">米</option>
                    <option value="cm">厘米</option>
                </select>
                <input type="number" id="value" placeholder="数值">
                <select id="toUnit">
                    <option value="m">米</option>
                    <option value="cm">厘米</option>
                </select>
                <button onclick="convert()">转换</button>
                '''
        
        return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{tool_type.title()}工具</title>
</head>
<body>
    <div id="toolContainer">
        <h1>{tool_type.title()}工具</h1>
        {interactive_elements}
    </div>
    <script>
    function calculate() {{ console.log('计算'); }}
    function save() {{ console.log('保存'); }}
    function convert() {{ console.log('转换'); }}
    </script>
</body>
</html>'''


# 运行测试的辅助函数
if __name__ == "__main__":
    pytest.main([__file__, "-v"])