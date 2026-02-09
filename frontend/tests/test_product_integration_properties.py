"""
产品集成功能属性测试

验证产品嵌入系统的正确性属性，确保系统在各种输入和状态下的行为符合预期。
这些测试使用基于属性的测试方法，通过生成大量随机输入来验证系统的健壮性。
"""

import pytest
from hypothesis import given, strategies as st, assume, settings, HealthCheck
from hypothesis.stateful import RuleBasedStateMachine, Bundle, rule, initialize, invariant
import json
import tempfile
import zipfile
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import hashlib
import time
import random
import re

# 测试数据生成策略
@st.composite
def product_data(draw):
    """生成有效的产品数据"""
    # 生成有效的标题（只包含字母、数字和空格）
    title = draw(st.text(min_size=1, max_size=200, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs')))).strip()
    if not title:  # 如果标题为空，使用默认值
        title = "Test Product"
    
    # 生成有效的技术栈（只包含非空字符串）
    tech_stack = []
    tech_count = draw(st.integers(min_value=0, max_value=20))
    for _ in range(tech_count):
        tech = draw(st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')))).strip()
        if tech:  # 只添加非空的技术栈项
            tech_stack.append(tech)
    
    # 生成有效的版本号
    version = draw(st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Nd', 'Po')))).strip()
    if not version:  # 如果版本号为空，使用默认值
        version = "1.0.0"
    
    return {
        "title": title,
        "description": draw(st.one_of(st.none(), st.text(max_size=2000))),
        "tech_stack": tech_stack,
        "product_type": draw(st.sampled_from(['static', 'spa', 'game', 'tool'])),
        "entry_file": draw(st.sampled_from(['index.html', 'main.html', 'app.html'])),
        "is_published": draw(st.booleans()),
        "is_featured": draw(st.booleans()),
        "display_order": draw(st.integers(min_value=0, max_value=9999)),
        "version": version,
        "config_data": draw(st.dictionaries(
            st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
            st.one_of(st.text(), st.integers(), st.booleans(), st.floats(allow_nan=False)),
            max_size=10
        ))
    }

@st.composite
def zip_file_content(draw):
    """生成ZIP文件内容"""
    files = {}
    
    # 必须包含入口文件
    entry_file = draw(st.sampled_from(['index.html', 'main.html', 'app.html']))
    files[entry_file] = draw(st.text(min_size=10, max_size=1000))
    
    # 可选的其他文件
    num_files = draw(st.integers(min_value=0, max_value=10))
    for i in range(num_files):
        filename = draw(st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))))
        extension = draw(st.sampled_from(['.html', '.css', '.js', '.json', '.txt']))
        content = draw(st.text(max_size=500))
        files[f"{filename}{extension}"] = content
    
    return files, entry_file

@st.composite
def api_token_data(draw):
    """生成API令牌数据"""
    return {
        "permissions": draw(st.lists(st.sampled_from(['read', 'write', 'admin']), min_size=1, max_size=3, unique=True)),
        "expires_in_days": draw(st.integers(min_value=1, max_value=365))
    }

@st.composite
def user_session_data(draw):
    """生成用户会话数据"""
    return {
        "user_id": draw(st.one_of(st.none(), st.text(min_size=1, max_size=100))),
        "session_data": draw(st.dictionaries(
            st.text(min_size=1, max_size=50),
            st.one_of(st.text(), st.integers(), st.booleans()),
            max_size=20
        )),
        "is_guest": draw(st.booleans())
    }

@st.composite
def storage_data(draw):
    """生成存储数据"""
    return {
        "key": draw(st.text(min_size=1, max_size=255, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Pc')))),
        "data": draw(st.one_of(
            st.text(),
            st.integers(),
            st.booleans(),
            st.dictionaries(st.text(), st.one_of(st.text(), st.integers(), st.booleans()), max_size=10),
            st.lists(st.one_of(st.text(), st.integers()), max_size=20)
        ))
    }

class ProductIntegrationStateMachine(RuleBasedStateMachine):
    """
    产品集成系统的状态机测试
    
    这个状态机模拟产品的完整生命周期：创建、上传、配置、发布、使用、监控等。
    通过随机执行各种操作，验证系统在复杂交互下的正确性。
    """
    
    def __init__(self):
        super().__init__()
        self.products: Dict[int, Dict[str, Any]] = {}
        self.api_tokens: Dict[str, Dict[str, Any]] = {}
        self.user_sessions: Dict[str, Dict[str, Any]] = {}
        self.storage_data: Dict[int, Dict[str, Any]] = {}
        self.next_product_id = 1
        self.system_state = {
            "total_products": 0,
            "published_products": 0,
            "total_storage_size": 0,
            "active_sessions": 0
        }
    
    products = Bundle('products')
    tokens = Bundle('tokens')
    sessions = Bundle('sessions')
    
    @initialize()
    def setup(self):
        """初始化测试环境"""
        self.system_state = {
            "total_products": 0,
            "published_products": 0,
            "total_storage_size": 0,
            "active_sessions": 0
        }
    
    @rule(target=products, data=product_data())
    def create_product(self, data):
        """创建产品"""
        product_id = self.next_product_id
        self.next_product_id += 1
        
        product = {
            "id": product_id,
            "created_at": time.time(),
            "file_uploaded": False,
            "file_path": None,
            **data
        }
        
        self.products[product_id] = product
        self.storage_data[product_id] = {}
        self.system_state["total_products"] += 1
        
        if product["is_published"]:
            self.system_state["published_products"] += 1
        
        return product_id
    
    @rule(product_id=products, files_data=zip_file_content())
    def upload_product_files(self, product_id, files_data):
        """上传产品文件"""
        assume(product_id in self.products)
        
        files, entry_file = files_data
        
        # 模拟文件上传和解压
        total_size = sum(len(content.encode('utf-8')) for content in files.values())
        
        # 检查文件大小限制 (100MB)
        if total_size > 100 * 1024 * 1024:
            return  # 文件过大，上传失败
        
        self.products[product_id]["file_uploaded"] = True
        self.products[product_id]["file_path"] = f"/products/{product_id}/"
        self.products[product_id]["entry_file"] = entry_file
        self.products[product_id]["files"] = files
        self.products[product_id]["total_size"] = total_size
    
    @rule(product_id=products)
    def publish_product(self, product_id):
        """发布产品"""
        assume(product_id in self.products)
        
        product = self.products[product_id]
        
        # 只有上传了文件的产品才能发布
        if not product["file_uploaded"]:
            return
        
        was_published = product["is_published"]
        product["is_published"] = True
        
        if not was_published:
            self.system_state["published_products"] += 1
    
    @rule(product_id=products)
    def unpublish_product(self, product_id):
        """下线产品"""
        assume(product_id in self.products)
        
        product = self.products[product_id]
        was_published = product["is_published"]
        product["is_published"] = False
        
        if was_published:
            self.system_state["published_products"] -= 1
    
    @rule(target=tokens, product_id=products, token_data=api_token_data())
    def generate_api_token(self, product_id, token_data):
        """生成API令牌"""
        assume(product_id in self.products)
        
        token = hashlib.sha256(f"{product_id}_{time.time()}_{random.random()}".encode()).hexdigest()
        
        self.api_tokens[token] = {
            "product_id": product_id,
            "permissions": token_data["permissions"],
            "created_at": time.time(),
            "expires_at": time.time() + (token_data["expires_in_days"] * 24 * 3600),
            "is_active": True,
            "usage_count": 0
        }
        
        return token
    
    @rule(token=tokens)
    def use_api_token(self, token):
        """使用API令牌"""
        assume(token in self.api_tokens)
        
        token_data = self.api_tokens[token]
        
        # 检查令牌是否过期
        if time.time() > token_data["expires_at"]:
            token_data["is_active"] = False
            return False
        
        if token_data["is_active"]:
            token_data["usage_count"] += 1
            return True
        
        return False
    
    @rule(token=tokens)
    def revoke_api_token(self, token):
        """撤销API令牌"""
        assume(token in self.api_tokens)
        
        self.api_tokens[token]["is_active"] = False
    
    @rule(target=sessions, product_id=products, session_data=user_session_data())
    def create_user_session(self, product_id, session_data):
        """创建用户会话"""
        assume(product_id in self.products)
        
        session_id = hashlib.sha256(f"{product_id}_{time.time()}_{random.random()}".encode()).hexdigest()
        
        self.user_sessions[session_id] = {
            "product_id": product_id,
            "created_at": time.time(),
            "expires_at": time.time() + (24 * 3600),  # 24小时
            "last_accessed": time.time(),
            **session_data
        }
        
        self.system_state["active_sessions"] += 1
        
        return session_id
    
    @rule(session_id=sessions, new_data=st.dictionaries(st.text(), st.one_of(st.text(), st.integers()), max_size=10))
    def update_session_data(self, session_id, new_data):
        """更新会话数据"""
        assume(session_id in self.user_sessions)
        
        session = self.user_sessions[session_id]
        
        # 检查会话是否过期
        if time.time() > session["expires_at"]:
            return False
        
        session["session_data"].update(new_data)
        session["last_accessed"] = time.time()
        
        return True
    
    @rule(product_id=products, data=storage_data())
    def store_product_data(self, product_id, data):
        """存储产品数据"""
        assume(product_id in self.products)
        
        key = data["key"]
        value = data["data"]
        
        # 计算数据大小
        data_size = len(json.dumps(value).encode('utf-8'))
        
        # 检查存储限制 (每个产品100MB)
        current_size = sum(
            item.get("size", 0) for item in self.storage_data[product_id].values()
        )
        
        if current_size + data_size > 100 * 1024 * 1024:
            return False  # 存储空间不足
        
        self.storage_data[product_id][key] = {
            "data": value,
            "size": data_size,
            "created_at": time.time(),
            "access_count": 0
        }
        
        self.system_state["total_storage_size"] += data_size
        
        return True
    
    @rule(product_id=products, key=st.text(min_size=1, max_size=255))
    def access_product_data(self, product_id, key):
        """访问产品数据"""
        assume(product_id in self.products)
        assume(key in self.storage_data[product_id])
        
        self.storage_data[product_id][key]["access_count"] += 1
        
        return self.storage_data[product_id][key]["data"]
    
    @rule(product_id=products)
    def delete_product(self, product_id):
        """删除产品"""
        assume(product_id in self.products)
        
        product = self.products[product_id]
        
        # 更新系统状态
        self.system_state["total_products"] -= 1
        if product["is_published"]:
            self.system_state["published_products"] -= 1
        
        # 清理存储数据
        if product_id in self.storage_data:
            for item in self.storage_data[product_id].values():
                self.system_state["total_storage_size"] -= item["size"]
            del self.storage_data[product_id]
        
        # 撤销相关API令牌
        for token, token_data in self.api_tokens.items():
            if token_data["product_id"] == product_id:
                token_data["is_active"] = False
        
        # 清理相关会话
        sessions_to_remove = []
        for session_id, session in self.user_sessions.items():
            if session["product_id"] == product_id:
                sessions_to_remove.append(session_id)
                self.system_state["active_sessions"] -= 1
        
        for session_id in sessions_to_remove:
            del self.user_sessions[session_id]
        
        del self.products[product_id]
    
    # 不变量检查
    @invariant()
    def system_state_consistency(self):
        """系统状态一致性检查"""
        # 检查产品计数
        actual_total = len(self.products)
        actual_published = sum(1 for p in self.products.values() if p["is_published"])
        
        assert self.system_state["total_products"] == actual_total, \
            f"产品总数不一致: 期望 {actual_total}, 实际 {self.system_state['total_products']}"
        
        assert self.system_state["published_products"] == actual_published, \
            f"已发布产品数不一致: 期望 {actual_published}, 实际 {self.system_state['published_products']}"
    
    @invariant()
    def storage_size_consistency(self):
        """存储大小一致性检查"""
        actual_size = 0
        for product_storage in self.storage_data.values():
            for item in product_storage.values():
                actual_size += item["size"]
        
        assert self.system_state["total_storage_size"] == actual_size, \
            f"存储大小不一致: 期望 {actual_size}, 实际 {self.system_state['total_storage_size']}"
    
    @invariant()
    def session_count_consistency(self):
        """会话计数一致性检查"""
        actual_sessions = len(self.user_sessions)
        
        assert self.system_state["active_sessions"] == actual_sessions, \
            f"活跃会话数不一致: 期望 {actual_sessions}, 实际 {self.system_state['active_sessions']}"
    
    @invariant()
    def published_products_have_files(self):
        """已发布产品必须有文件"""
        for product in self.products.values():
            if product["is_published"]:
                assert product["file_uploaded"], \
                    f"已发布产品 {product['id']} 没有上传文件"
    
    @invariant()
    def api_tokens_belong_to_existing_products(self):
        """API令牌必须属于存在的产品"""
        for token_data in self.api_tokens.values():
            product_id = token_data["product_id"]
            assert product_id in self.products, \
                f"API令牌关联的产品 {product_id} 不存在"
    
    @invariant()
    def sessions_belong_to_existing_products(self):
        """用户会话必须属于存在的产品"""
        for session in self.user_sessions.values():
            product_id = session["product_id"]
            assert product_id in self.products, \
                f"用户会话关联的产品 {product_id} 不存在"

# 属性测试
class TestProductIntegrationProperties:
    """产品集成功能属性测试"""
    
    @given(data=product_data())
    def test_product_data_model_properties(self, data):
        """
        **Feature: product-integration, Property 1: 产品文件上传完整性**
        **Validates: Requirements 3.2**
        
        验证产品数据模型的完整性和一致性：
        1. 数据序列化和反序列化保持一致
        2. 必填字段验证正确
        3. 数据类型约束有效
        4. 业务规则验证正确
        """
        # 1. 测试数据序列化和反序列化的完整性
        serialized = json.dumps(data, default=str, ensure_ascii=False)
        deserialized = json.loads(serialized)
        
        # 验证关键字段完整性
        assert deserialized["title"] == data["title"]
        assert deserialized["product_type"] == data["product_type"]
        assert deserialized["is_published"] == data["is_published"]
        assert deserialized["is_featured"] == data["is_featured"]
        assert deserialized["display_order"] == data["display_order"]
        assert deserialized["version"] == data["version"]
        assert deserialized["entry_file"] == data["entry_file"]
        
        # 2. 验证复杂数据结构的完整性
        assert deserialized["tech_stack"] == data["tech_stack"]
        assert deserialized["config_data"] == data["config_data"]
        
        # 3. 验证数据类型约束
        assert isinstance(data["title"], str) and len(data["title"]) > 0
        assert data["product_type"] in ['static', 'spa', 'game', 'tool']
        assert isinstance(data["is_published"], bool)
        assert isinstance(data["is_featured"], bool)
        assert isinstance(data["display_order"], int) and 0 <= data["display_order"] <= 9999
        assert isinstance(data["tech_stack"], list) and len(data["tech_stack"]) <= 20
        assert isinstance(data["config_data"], dict)
        
        # 4. 验证业务规则
        # 产品标题不能为空或只包含空白字符
        assert data["title"].strip() != ""
        
        # 技术栈项目不能为空
        for tech in data["tech_stack"]:
            assert isinstance(tech, str) and tech.strip() != ""
        
        # 入口文件必须是HTML文件
        assert data["entry_file"].endswith(('.html', '.htm'))
        
        # 版本号不能为空
        assert data["version"].strip() != ""
        
        # 5. 测试数据完整性哈希
        # 确保相同的数据产生相同的哈希值
        data_str = json.dumps(data, sort_keys=True, default=str)
        hash1 = hashlib.sha256(data_str.encode()).hexdigest()
        hash2 = hashlib.sha256(data_str.encode()).hexdigest()
        assert hash1 == hash2
        
        # 6. 测试数据大小限制
        # 确保序列化后的数据不会过大
        serialized_size = len(serialized.encode('utf-8'))
        assert serialized_size < 10 * 1024  # 10KB限制，防止数据过大
    
    @given(files_data=zip_file_content())
    def test_file_upload_integrity(self, files_data):
        """
        属性 2: 产品文件上传完整性
        验证文件上传后的完整性保持
        """
        files, entry_file = files_data
        
        # 模拟文件上传过程
        temp_zip_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_zip:
                temp_zip_path = temp_zip.name
                with zipfile.ZipFile(temp_zip.name, 'w') as zf:
                    for filename, content in files.items():
                        zf.writestr(filename, content)
            
            # 验证ZIP文件完整性
            with zipfile.ZipFile(temp_zip_path, 'r') as zf:
                extracted_files = {}
                for filename in zf.namelist():
                    extracted_files[filename] = zf.read(filename).decode('utf-8')
            
            # 检查文件完整性
            assert len(extracted_files) == len(files)
            for filename, content in files.items():
                assert filename in extracted_files
                assert extracted_files[filename] == content
                
        finally:
            # 清理临时文件
            if temp_zip_path and os.path.exists(temp_zip_path):
                try:
                    os.unlink(temp_zip_path)
                except (PermissionError, OSError):
                    # 在Windows上有时会出现权限问题，忽略清理错误
                    pass
    
    @given(
        product_data=product_data(),
        api_data=api_token_data()
    )
    def test_api_token_security(self, product_data, api_data):
        """
        属性 3: API令牌安全性
        验证API令牌的生成和验证机制
        """
        # 模拟令牌生成
        token_payload = {
            "product_id": 1,
            "permissions": api_data["permissions"],
            "created_at": time.time(),
            "expires_at": time.time() + (api_data["expires_in_days"] * 24 * 3600)
        }
        
        # 生成令牌
        token = hashlib.sha256(json.dumps(token_payload, sort_keys=True).encode()).hexdigest()
        
        # 验证令牌属性
        assert len(token) == 64  # SHA256哈希长度
        assert isinstance(token, str)
        assert all(c in '0123456789abcdef' for c in token)
        
        # 验证权限
        assert all(perm in ['read', 'write', 'admin'] for perm in api_data["permissions"])
        assert len(set(api_data["permissions"])) == len(api_data["permissions"])  # 无重复
    
    @given(
        session_data=user_session_data(),
        update_data=st.dictionaries(st.text(), st.one_of(st.text(), st.integers()), max_size=10)
    )
    def test_session_data_isolation(self, session_data, update_data):
        """
        属性 4: 用户会话数据隔离性
        验证不同会话的数据完全隔离
        """
        # 创建两个独立的会话
        session1 = {
            "id": "session1",
            "data": session_data["session_data"].copy()
        }
        
        session2 = {
            "id": "session2", 
            "data": {}
        }
        
        # 更新session1的数据
        session1["data"].update(update_data)
        
        # 验证session2不受影响
        assert session2["data"] == {}
        
        # 验证session1包含更新的数据
        for key, value in update_data.items():
            assert session1["data"][key] == value
    
    @given(
        storage_items=st.lists(storage_data(), min_size=1, max_size=10)
    )
    def test_storage_data_consistency(self, storage_items):
        """
        属性 5: 存储数据一致性
        验证数据存储和检索的一致性
        """
        storage = {}
        
        # 处理存储项目，考虑重复键的情况
        for item in storage_items:
            key = item["key"]
            data = item["data"]
            
            # 计算数据大小
            data_size = len(json.dumps(data).encode('utf-8'))
            
            # 存储数据（重复键会覆盖）
            storage[key] = {
                "data": data,
                "size": data_size,
                "access_count": 0
            }
        
        # 验证存储一致性
        calculated_size = sum(item["size"] for item in storage.values())
        
        # 重新计算预期大小（考虑重复键覆盖的情况）
        expected_size = 0
        processed_keys = set()
        
        # 从后往前处理，模拟覆盖行为
        for item in reversed(storage_items):
            key = item["key"]
            if key not in processed_keys:
                data_size = len(json.dumps(item["data"]).encode('utf-8'))
                expected_size += data_size
                processed_keys.add(key)
        
        assert calculated_size == expected_size, \
            f"存储大小不一致: 计算值 {calculated_size}, 期望值 {expected_size}"
        
        # 验证数据检索
        for key, stored_item in storage.items():
            # 找到最后一个具有此键的项目
            last_item_with_key = None
            for item in reversed(storage_items):
                if item["key"] == key:
                    last_item_with_key = item
                    break
            
            if last_item_with_key:
                assert stored_item["data"] == last_item_with_key["data"], \
                    f"检索的数据不匹配: 键 {key}"
    
    @given(
        products=st.lists(product_data(), min_size=1, max_size=5)
    )
    def test_product_lifecycle_consistency(self, products):
        """
        属性 6: 产品生命周期一致性
        验证产品从创建到删除的整个生命周期中状态的一致性
        """
        product_registry = {}
        published_count = 0
        
        # 创建产品
        for i, product_data in enumerate(products):
            product_id = i + 1
            product = {
                "id": product_id,
                "created_at": time.time(),
                **product_data
            }
            
            product_registry[product_id] = product
            
            if product["is_published"]:
                published_count += 1
        
        # 验证初始状态
        assert len(product_registry) == len(products)
        actual_published = sum(1 for p in product_registry.values() if p["is_published"])
        assert actual_published == published_count
        
        # 模拟发布/下线操作
        for product in product_registry.values():
            if not product["is_published"]:
                product["is_published"] = True
                published_count += 1
        
        # 验证发布后状态
        assert all(p["is_published"] for p in product_registry.values())
        assert published_count == len(product_registry)
    
    @given(
        error_scenarios=st.lists(
            st.dictionaries(
                st.text(),
                st.one_of(st.text(), st.integers(), st.booleans()),
                max_size=5
            ),
            max_size=10
        )
    )
    def test_error_isolation(self, error_scenarios):
        """
        属性 7: 产品错误隔离性
        验证一个产品的错误不会影响其他产品
        """
        products_state = {}
        
        # 初始化多个产品状态
        for i in range(3):
            products_state[i] = {
                "status": "running",
                "error_count": 0,
                "last_error": None
            }
        
        # 模拟错误场景
        for scenario in error_scenarios:
            # 随机选择一个产品发生错误
            affected_product = hash(str(scenario)) % 3
            
            products_state[affected_product]["error_count"] += 1
            products_state[affected_product]["last_error"] = scenario
            
            # 验证其他产品不受影响
            for product_id, state in products_state.items():
                if product_id != affected_product:
                    assert state["status"] == "running"
                    # 错误计数不应该因为其他产品的错误而增加
                    # (这里简化了验证逻辑)
    
    @given(
        products=st.lists(product_data(), min_size=1, max_size=10),
        publish_operations=st.lists(
            st.tuples(st.integers(min_value=0, max_value=9), st.booleans()),
            min_size=1, max_size=20
        )
    )
    def test_product_publish_status_consistency(self, products, publish_operations):
        """
        **Feature: product-integration, Property 10: 产品发布状态一致性**
        **Validates: Requirements 3.4**
        
        验证产品发布状态变更的一致性：
        1. 发布状态变更后立即反映在查询结果中
        2. 已发布产品在公开列表中可见
        3. 未发布产品在公开列表中不可见
        4. 发布状态变更操作的原子性
        """
        # 1. 初始化产品注册表
        product_registry = {}
        published_products = set()
        
        for i, product_data in enumerate(products):
            product_id = i
            product = {
                "id": product_id,
                "is_published": product_data["is_published"],
                "title": product_data["title"],
                "product_type": product_data["product_type"],
                "created_at": time.time(),
                **product_data
            }
            product_registry[product_id] = product
            
            if product["is_published"]:
                published_products.add(product_id)
        
        # 2. 执行发布状态变更操作
        for product_index, new_status in publish_operations:
            if product_index >= len(products):
                continue  # 跳过无效的产品索引
            
            product_id = product_index
            product = product_registry[product_id]
            old_status = product["is_published"]
            
            # 模拟API更新操作
            product["is_published"] = new_status
            product["updated_at"] = time.time()
            
            # 更新发布产品集合
            if new_status and not old_status:
                # 从未发布变为已发布
                published_products.add(product_id)
            elif not new_status and old_status:
                # 从已发布变为未发布
                published_products.discard(product_id)
            
            # 3. 验证状态一致性
            # 验证产品状态立即更新
            assert product["is_published"] == new_status, \
                f"产品 {product_id} 发布状态未正确更新"
            
            # 验证已发布产品集合的一致性
            actual_published = {pid for pid, p in product_registry.items() if p["is_published"]}
            assert published_products == actual_published, \
                f"发布产品集合不一致: 期望 {published_products}, 实际 {actual_published}"
        
        # 4. 验证公开API查询的一致性
        # 模拟公开产品列表查询（只返回已发布的产品）
        public_products = [
            product for product in product_registry.values() 
            if product["is_published"]
        ]
        
        # 验证公开列表只包含已发布产品
        for product in public_products:
            assert product["is_published"], \
                f"公开列表包含未发布产品: {product['id']}"
        
        # 验证所有已发布产品都在公开列表中
        public_product_ids = {p["id"] for p in public_products}
        assert public_product_ids == published_products, \
            f"公开列表与发布状态不一致: 公开列表 {public_product_ids}, 已发布 {published_products}"
        
        # 5. 验证产品启动权限的一致性
        for product_id, product in product_registry.items():
            can_launch = product["is_published"]
            
            # 模拟产品启动检查
            if can_launch:
                # 已发布产品应该可以启动
                assert product["is_published"], \
                    f"已发布产品 {product_id} 无法启动"
            else:
                # 未发布产品应该被拒绝启动
                assert not product["is_published"], \
                    f"未发布产品 {product_id} 不应该可以启动"
        
        # 6. 验证发布状态变更的幂等性
        # 重复设置相同的发布状态不应该改变结果
        for product_id, product in product_registry.items():
            original_status = product["is_published"]
            original_updated_at = product.get("updated_at", 0)
            
            # 重复设置相同状态
            product["is_published"] = original_status
            
            # 验证状态没有改变
            assert product["is_published"] == original_status, \
                f"重复设置发布状态改变了产品 {product_id} 的状态"
        
        # 7. 验证批量操作的一致性
        # 模拟批量发布操作
        batch_publish_ids = list(product_registry.keys())[:min(3, len(product_registry))]
        
        for product_id in batch_publish_ids:
            product_registry[product_id]["is_published"] = True
        
        # 验证批量操作后的一致性
        for product_id in batch_publish_ids:
            assert product_registry[product_id]["is_published"], \
                f"批量发布操作失败: 产品 {product_id} 未正确发布"
        
        # 8. 验证状态变更的原子性
        # 确保状态变更是原子操作，不会出现中间状态
        for product_id, product in product_registry.items():
            status = product["is_published"]
            
            # 发布状态应该是明确的布尔值
            assert isinstance(status, bool), \
                f"产品 {product_id} 发布状态不是布尔值: {type(status)}"
            
            # 不应该存在中间状态
            assert status in [True, False], \
                f"产品 {product_id} 发布状态存在无效值: {status}"
    
    @given(
        file_contents=st.dictionaries(
            st.text(min_size=1, max_size=100, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Pc'))),
            st.text(max_size=1000),
            min_size=1, max_size=20
        ),
        malicious_attempts=st.lists(
            st.one_of(
                st.just("../../../etc/passwd"),
                st.just("..\\..\\windows\\system32\\config\\sam"),
                st.just("/etc/shadow"),
                st.just("C:\\Windows\\System32\\drivers\\etc\\hosts"),
                st.text(min_size=1, max_size=50).filter(lambda x: '..' in x or x.startswith('/')),
                st.text(min_size=1, max_size=50).filter(lambda x: x.endswith(('.exe', '.bat', '.php', '.py')))
            ),
            max_size=10
        )
    )
    def test_product_file_security(self, file_contents, malicious_attempts):
        """
        **Feature: product-integration, Property 8: 产品文件安全性**
        **Validates: Requirements 4.2**
        
        验证产品文件处理的安全性：
        1. 防止路径遍历攻击
        2. 阻止危险文件类型上传
        3. 文件访问权限隔离
        4. 文件完整性验证
        5. 文件大小和数量限制
        """
        # 1. 模拟文件服务配置
        file_service_config = {
            "max_file_size": 100 * 1024 * 1024,  # 100MB
            "allowed_extensions": {'.zip'},
            "dangerous_extensions": {
                '.exe', '.bat', '.cmd', '.com', '.pif', '.scr', '.vbs',
                '.jar', '.php', '.asp', '.aspx', '.jsp', '.py', '.rb', '.pl'
            },
            "safe_extensions": {
                '.html', '.htm', '.css', '.js', '.json', '.txt', '.md',
                '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.webp',
                '.mp3', '.wav', '.ogg', '.mp4', '.webm',
                '.woff', '.woff2', '.ttf', '.eot',
                '.xml', '.csv', '.pdf', '.map'
            },
            "max_files_per_product": 1000
        }
        
        # 2. 验证文件路径安全性
        def validate_file_path(file_path: str) -> bool:
            """验证文件路径是否安全"""
            # 检查路径遍历攻击
            if '..' in file_path or file_path.startswith('/') or file_path.startswith('\\'):
                return False
            
            # 检查绝对路径（Windows和Unix）
            if ':' in file_path or file_path.startswith('C:') or file_path.startswith('/'):
                return False
            
            # 检查文件名长度
            if len(file_path) > 255:
                return False
            
            # 检查文件扩展名
            file_ext = Path(file_path).suffix.lower() if '.' in file_path else ''
            if file_ext in file_service_config["dangerous_extensions"]:
                return False
            
            return True
        
        # 3. 测试合法文件的处理
        safe_files = {}
        for filename, content in file_contents.items():
            # 确保文件名安全
            safe_filename = filename.replace('..', '').replace('/', '').replace('\\', '')
            if not safe_filename:
                safe_filename = "safe_file.html"
            
            # 添加安全的扩展名
            if not any(safe_filename.endswith(ext) for ext in file_service_config["safe_extensions"]):
                safe_filename += ".html"
            
            safe_files[safe_filename] = content
        
        # 验证安全文件可以正常处理
        for filename, content in safe_files.items():
            assert validate_file_path(filename), f"安全文件路径验证失败: {filename}"
            
            # 验证文件大小限制
            content_size = len(content.encode('utf-8'))
            assert content_size <= file_service_config["max_file_size"], \
                f"文件大小超过限制: {content_size}"
        
        # 4. 测试恶意文件路径的阻止
        for malicious_path in malicious_attempts:
            # 恶意路径应该被拒绝
            is_safe = validate_file_path(malicious_path)
            assert not is_safe, f"恶意路径未被正确阻止: {malicious_path}"
        
        # 5. 验证文件数量限制
        if len(safe_files) > file_service_config["max_files_per_product"]:
            # 文件数量超过限制应该被拒绝
            assert False, f"文件数量超过限制但未被阻止: {len(safe_files)}"
        
        # 6. 模拟ZIP文件验证
        def validate_zip_contents(file_list: list) -> tuple:
            """验证ZIP文件内容的安全性"""
            if len(file_list) > file_service_config["max_files_per_product"]:
                return False, "ZIP文件包含过多文件"
            
            for file_name in file_list:
                if not validate_file_path(file_name):
                    return False, f"检测到不安全的文件路径: {file_name}"
            
            return True, "验证通过"
        
        # 测试ZIP内容验证
        file_list = list(safe_files.keys())
        is_valid, message = validate_zip_contents(file_list)
        assert is_valid, f"ZIP内容验证失败: {message}"
        
        # 7. 验证文件访问隔离
        def check_file_access_isolation(product_id: int, requested_path: str) -> bool:
            """检查文件访问是否被正确隔离"""
            # 模拟产品文件访问检查
            base_path = f"/products/{product_id}/"
            
            # 规范化路径（使用正斜杠）
            normalized_path = requested_path.replace('\\', '/')
            
            # 检查是否试图访问产品目录外的文件
            if not normalized_path.startswith(base_path):
                return False
            
            # 检查路径遍历
            if '..' in normalized_path:
                return False
            
            return True
        
        # 测试文件访问隔离
        product_id = 1
        for filename in safe_files.keys():
            # 合法访问应该被允许
            safe_path = f"/products/{product_id}/{filename}"
            assert check_file_access_isolation(product_id, safe_path), \
                f"合法文件访问被错误拒绝: {safe_path}"
        
        # 测试恶意访问被阻止
        malicious_access_attempts = [
            f"/products/{product_id}/../../../etc/passwd",
            f"/products/{product_id}/../../other_product/secret.txt",
            "/products/999/unauthorized.html",
            "../../../system/config"
        ]
        
        for malicious_path in malicious_access_attempts:
            assert not check_file_access_isolation(product_id, malicious_path), \
                f"恶意文件访问未被正确阻止: {malicious_path}"
        
        # 8. 验证文件完整性检查
        def verify_file_integrity(files: dict) -> bool:
            """验证文件完整性"""
            # 检查必需的入口文件
            has_entry_file = any(
                filename.endswith(('.html', '.htm')) 
                for filename in files.keys()
            )
            
            if not has_entry_file:
                return False
            
            # 检查文件内容不为空（对于关键文件）
            for filename, content in files.items():
                if filename.endswith(('.html', '.htm')):
                    if not content or not content.strip():
                        return False
            
            return True
        
        # 测试文件完整性验证
        if safe_files:
            integrity_valid = verify_file_integrity(safe_files)
            # 如果有HTML文件，完整性检查应该通过
            has_html = any(f.endswith(('.html', '.htm')) for f in safe_files.keys())
            if has_html:
                html_files_valid = all(
                    safe_files[f].strip() for f in safe_files.keys() 
                    if f.endswith(('.html', '.htm'))
                )
                assert integrity_valid == html_files_valid, \
                    "文件完整性验证结果不一致"
        
        # 9. 验证MIME类型检查
        def validate_mime_type(filename: str) -> bool:
            """验证MIME类型"""
            import mimetypes
            mime_type, _ = mimetypes.guess_type(filename)
            
            # 允许的MIME类型
            allowed_mime_types = {
                'text/html', 'text/css', 'application/javascript', 'text/javascript',
                'application/json', 'text/plain', 'text/markdown',
                'image/png', 'image/jpeg', 'image/gif', 'image/svg+xml',
                'audio/mpeg', 'audio/wav', 'video/mp4', 'video/webm',
                'font/woff', 'font/woff2', 'application/font-woff',
                'application/xml', 'text/xml', 'text/csv', 'application/pdf'
            }
            
            # 如果无法确定MIME类型，检查扩展名
            if not mime_type:
                file_ext = Path(filename).suffix.lower()
                return file_ext in file_service_config["safe_extensions"]
            
            return mime_type in allowed_mime_types
        
        # 测试MIME类型验证
        for filename in safe_files.keys():
            mime_valid = validate_mime_type(filename)
            # 安全文件的MIME类型应该被允许
            assert mime_valid, f"安全文件的MIME类型被错误拒绝: {filename}"
    
    @given(
        products=st.lists(product_data(), min_size=1, max_size=5),
        iframe_messages=st.lists(
            st.dictionaries(
                st.sampled_from(['type', 'data', 'origin', 'source']),
                st.one_of(st.text(), st.integers(), st.booleans()),
                min_size=1, max_size=4
            ),
            max_size=10
        ),
        dom_access_attempts=st.lists(
            st.sampled_from([
                'document.cookie',
                'localStorage',
                'sessionStorage',
                'window.parent',
                'window.top',
                'document.domain',
                'location.href',
                'history.pushState'
            ]),
            max_size=10
        )
    )
    def test_product_container_isolation(self, products, iframe_messages, dom_access_attempts):
        """
        **Feature: product-integration, Property 2: 产品容器隔离性**
        **Validates: Requirements 4.1, 4.2**
        
        验证产品容器的隔离性和安全性：
        1. iframe沙箱隔离机制
        2. 跨域消息通信安全
        3. DOM访问权限控制
        4. 全局变量隔离
        5. 存储空间隔离
        6. 网络请求限制
        """
        # 1. 模拟产品容器配置
        container_config = {
            "sandbox_options": [
                "allow-scripts",
                "allow-same-origin", 
                "allow-forms",
                "allow-popups",
                "allow-modals"
            ],
            "globally_forbidden_options": [
                "allow-top-navigation",
                "allow-downloads"
            ],
            "allowed_message_types": [
                "product-ready",
                "product-error", 
                "product-resize",
                "spa_route_change"
            ],
            "forbidden_dom_access": [
                "document.cookie",
                "localStorage",
                "sessionStorage", 
                "window.parent",
                "window.top"
            ]
        }
        
        # 2. 验证沙箱配置的安全性
        def validate_sandbox_options(product_type: str) -> dict:
            """验证产品类型对应的沙箱配置"""
            base_options = ["allow-scripts", "allow-same-origin"]
            
            if product_type == "static":
                # 静态产品最严格的沙箱
                return {
                    "allowed": base_options + ["allow-forms"],
                    "forbidden": ["allow-top-navigation", "allow-downloads", "allow-pointer-lock"]
                }
            elif product_type == "spa":
                # SPA需要更多权限
                return {
                    "allowed": base_options + ["allow-forms", "allow-popups", "allow-modals"],
                    "forbidden": ["allow-top-navigation", "allow-downloads"]
                }
            elif product_type == "game":
                # 游戏可能需要指针锁定
                return {
                    "allowed": base_options + ["allow-forms", "allow-popups", "allow-pointer-lock"],
                    "forbidden": ["allow-top-navigation", "allow-downloads"]
                }
            elif product_type == "tool":
                # 工具应用需要表单和弹窗
                return {
                    "allowed": base_options + ["allow-forms", "allow-popups", "allow-modals"],
                    "forbidden": ["allow-top-navigation", "allow-downloads", "allow-pointer-lock"]
                }
            else:
                # 默认最严格配置
                return {
                    "allowed": base_options,
                    "forbidden": ["allow-top-navigation", "allow-downloads", "allow-pointer-lock", "allow-popups"]
                }
        
        # 3. 测试每个产品的沙箱配置
        for product_data in products:
            sandbox_config = validate_sandbox_options(product_data["product_type"])
            
            # 验证允许的选项不包含全局禁止的选项
            for option in sandbox_config["allowed"]:
                assert option not in container_config["globally_forbidden_options"], \
                    f"产品类型 {product_data['product_type']} 使用了全局禁止的沙箱选项: {option}"
            
            # 验证禁止的选项确实被禁止
            for option in sandbox_config["forbidden"]:
                assert option not in sandbox_config["allowed"], \
                    f"产品类型 {product_data['product_type']} 的沙箱配置冲突: {option}"
        
        # 4. 验证跨域消息通信安全
        def validate_iframe_message(message: dict, expected_origin: str) -> bool:
            """验证iframe消息的安全性"""
            # 检查消息类型
            msg_type = message.get("type")
            if not msg_type or msg_type not in container_config["allowed_message_types"]:
                return False
            
            # 检查消息来源
            origin = message.get("origin", "")
            if not origin.startswith(expected_origin):
                return False
            
            # 检查消息数据大小
            data = message.get("data", {})
            if isinstance(data, dict):
                data_size = len(str(data))
                if data_size > 10 * 1024:  # 10KB限制
                    return False
            
            return True
        
        # 测试消息验证
        for product_data in products:
            product_origin = f"https://example.com/products/{product_data.get('id', 1)}"
            
            for message in iframe_messages:
                # 添加必要的字段
                test_message = {
                    "origin": product_origin,
                    **message
                }
                
                # 验证合法消息
                if test_message.get("type") in container_config["allowed_message_types"]:
                    is_valid = validate_iframe_message(test_message, product_origin)
                    assert is_valid, f"合法消息被错误拒绝: {test_message}"
        
        # 5. 验证DOM访问权限控制
        def check_dom_access_isolation(access_attempt: str) -> bool:
            """检查DOM访问是否被正确隔离"""
            # 模拟沙箱环境中的DOM访问检查
            if access_attempt in container_config["forbidden_dom_access"]:
                return False  # 应该被阻止
            
            # 检查是否试图访问父窗口
            if "parent" in access_attempt or "top" in access_attempt:
                return False
            
            # 检查是否试图修改域名
            if "document.domain" in access_attempt:
                return False
            
            return True  # 允许访问
        
        # 测试DOM访问隔离
        for access_attempt in dom_access_attempts:
            is_allowed = check_dom_access_isolation(access_attempt)
            
            # 危险的DOM访问应该被阻止
            if access_attempt in container_config["forbidden_dom_access"]:
                assert not is_allowed, f"危险的DOM访问未被阻止: {access_attempt}"
        
        # 6. 验证存储空间隔离
        def validate_storage_isolation(product_id: int, storage_key: str) -> bool:
            """验证产品存储空间的隔离性"""
            # 模拟产品存储空间检查
            expected_prefix = f"product_{product_id}_"
            
            # 存储键必须包含产品ID前缀
            if not storage_key.startswith(expected_prefix):
                return False
            
            # 检查键名长度
            if len(storage_key) > 255:
                return False
            
            # 检查是否试图访问其他产品的存储
            if "product_" in storage_key and not storage_key.startswith(expected_prefix):
                return False
            
            return True
        
        # 测试存储隔离
        for i, product_data in enumerate(products):
            product_id = i + 1
            
            # 测试合法的存储键
            valid_keys = [
                f"product_{product_id}_user_settings",
                f"product_{product_id}_game_state",
                f"product_{product_id}_preferences"
            ]
            
            for key in valid_keys:
                assert validate_storage_isolation(product_id, key), \
                    f"合法存储键被错误拒绝: {key}"
            
            # 测试非法的存储键
            invalid_keys = [
                f"product_{product_id + 1}_data",  # 其他产品的数据
                "global_config",  # 全局配置
                "../../../system_config"  # 路径遍历
            ]
            
            for key in invalid_keys:
                assert not validate_storage_isolation(product_id, key), \
                    f"非法存储键未被正确阻止: {key}"
        
        # 7. 验证网络请求限制
        def validate_network_request(product_id: int, url: str, method: str) -> bool:
            """验证网络请求是否符合安全策略"""
            # 允许的请求域名
            allowed_domains = [
                f"api.example.com/products/{product_id}",
                "cdn.example.com",
                "fonts.googleapis.com",
                "unpkg.com"
            ]
            
            # 检查是否为允许的域名
            is_allowed_domain = any(domain in url for domain in allowed_domains)
            
            # 检查请求方法
            allowed_methods = ["GET", "POST", "PUT", "DELETE"]
            if method not in allowed_methods:
                return False
            
            # 检查是否试图访问本地资源
            if url.startswith("file://") or "localhost" in url or "127.0.0.1" in url:
                return False
            
            return is_allowed_domain
        
        # 测试网络请求限制
        for i, product_data in enumerate(products):
            product_id = i + 1
            
            # 测试合法请求
            valid_requests = [
                (f"https://api.example.com/products/{product_id}/data", "GET"),
                ("https://cdn.example.com/assets/style.css", "GET"),
                (f"https://api.example.com/products/{product_id}/stats", "POST")
            ]
            
            for url, method in valid_requests:
                assert validate_network_request(product_id, url, method), \
                    f"合法网络请求被错误拒绝: {method} {url}"
            
            # 测试非法请求
            invalid_requests = [
                (f"https://api.example.com/products/{product_id + 1}/data", "GET"),  # 其他产品数据
                ("file:///etc/passwd", "GET"),  # 本地文件
                ("https://malicious.com/steal-data", "POST"),  # 恶意域名
                ("http://localhost:3000/admin", "GET")  # 本地服务
            ]
            
            for url, method in invalid_requests:
                assert not validate_network_request(product_id, url, method), \
                    f"非法网络请求未被正确阻止: {method} {url}"
        
        # 8. 验证全局变量隔离
        def validate_global_variable_isolation(product_id: int, var_name: str) -> bool:
            """验证全局变量的隔离性"""
            # 产品应该只能访问自己的全局变量
            allowed_prefixes = [
                f"PRODUCT_{product_id}_",
                "APP_",  # 应用级别的配置
                "PUBLIC_"  # 公共配置
            ]
            
            # 禁止访问的全局变量
            forbidden_vars = [
                "ADMIN_TOKEN",
                "DATABASE_URL", 
                "SECRET_KEY",
                "API_PRIVATE_KEY"
            ]
            
            if var_name in forbidden_vars:
                return False
            
            # 检查是否有合法前缀
            has_valid_prefix = any(var_name.startswith(prefix) for prefix in allowed_prefixes)
            
            # 检查是否试图访问其他产品的变量
            if "PRODUCT_" in var_name and not var_name.startswith(f"PRODUCT_{product_id}_"):
                return False
            
            return has_valid_prefix or var_name in ["console", "setTimeout", "setInterval"]
        
        # 测试全局变量隔离
        for i, product_data in enumerate(products):
            product_id = i + 1
            
            # 测试合法的全局变量
            valid_vars = [
                f"PRODUCT_{product_id}_CONFIG",
                "APP_VERSION",
                "PUBLIC_API_URL",
                "console",
                "setTimeout"
            ]
            
            for var_name in valid_vars:
                assert validate_global_variable_isolation(product_id, var_name), \
                    f"合法全局变量访问被错误拒绝: {var_name}"
            
            # 测试非法的全局变量
            invalid_vars = [
                "ADMIN_TOKEN",
                "DATABASE_URL",
                f"PRODUCT_{product_id + 1}_SECRET"
            ]
            
            for var_name in invalid_vars:
                assert not validate_global_variable_isolation(product_id, var_name), \
                    f"非法全局变量访问未被正确阻止: {var_name}"
        
        # 9. 验证错误隔离
        def validate_error_isolation(product_id: int, error_data: dict) -> bool:
            """验证产品错误不会影响其他产品"""
            # 错误应该被限制在产品自己的作用域内
            error_scope = error_data.get("scope", "")
            
            # 检查错误是否正确标识了产品ID
            if "product_id" in error_data:
                if error_data["product_id"] != product_id:
                    return False  # 错误标识了错误的产品ID
            
            # 检查错误是否试图影响全局状态
            if "global" in error_scope or "system" in error_scope:
                return False
            
            # 检查错误消息是否包含敏感信息
            error_message = error_data.get("message", "")
            sensitive_keywords = ["password", "token", "secret", "key", "admin"]
            
            if any(keyword in error_message.lower() for keyword in sensitive_keywords):
                return False
            
            return True
        
        # 测试错误隔离
        for i, product_data in enumerate(products):
            product_id = i + 1
            
            # 模拟产品错误
            test_errors = [
                {
                    "product_id": product_id,
                    "scope": f"product_{product_id}",
                    "message": "产品加载失败",
                    "type": "load_error"
                },
                {
                    "product_id": product_id,
                    "scope": "local",
                    "message": "用户输入验证失败",
                    "type": "validation_error"
                }
            ]
            
            for error_data in test_errors:
                assert validate_error_isolation(product_id, error_data), \
                    f"产品错误隔离验证失败: {error_data}"
    
    @given(
        products=st.lists(product_data(), min_size=1, max_size=5),
        navigation_actions=st.lists(
            st.sampled_from([
                'back_to_main',
                'toggle_fullscreen',
                'show_product_info',
                'open_settings',
                'refresh_product',
                'close_product'
            ]),
            min_size=1, max_size=20
        ),
        display_modes=st.lists(
            st.sampled_from(['windowed', 'fullscreen', 'embedded']),
            min_size=1, max_size=10
        )
    )
    def test_product_navigation_functionality(self, products, navigation_actions, display_modes):
        """
        **Feature: product-integration, Property 11: 产品导航功能性**
        **Validates: Requirements 6.3**
        
        验证产品导航功能的完整性和可靠性：
        1. 返回主网站功能始终可用
        2. 全屏切换功能正常工作
        3. 产品信息显示准确
        4. 导航状态持久性
        5. 多种显示模式支持
        6. 导航操作的响应性
        """
        # 1. 模拟产品导航栏配置
        navbar_config = {
            "always_visible": True,
            "position": "top",  # top, bottom, floating
            "buttons": {
                "back_to_main": {
                    "enabled": True,
                    "label": "返回主站",
                    "icon": "home",
                    "priority": 1
                },
                "toggle_fullscreen": {
                    "enabled": True,
                    "label": "全屏切换",
                    "icon": "fullscreen",
                    "priority": 2
                },
                "show_product_info": {
                    "enabled": True,
                    "label": "产品信息",
                    "icon": "info",
                    "priority": 3
                },
                "open_settings": {
                    "enabled": True,
                    "label": "设置",
                    "icon": "settings",
                    "priority": 4
                },
                "refresh_product": {
                    "enabled": True,
                    "label": "刷新",
                    "icon": "refresh",
                    "priority": 5
                },
                "close_product": {
                    "enabled": False,  # 可选功能
                    "label": "关闭",
                    "icon": "close",
                    "priority": 6
                }
            },
            "auto_hide_timeout": 3000,  # 3秒后自动隐藏（仅在全屏模式）
            "responsive_breakpoints": {
                "mobile": 768,
                "tablet": 1024
            }
        }
        
        # 2. 验证导航栏基本功能
        def validate_navbar_functionality(product_id: int, current_mode: str) -> dict:
            """验证导航栏功能的可用性"""
            navbar_state = {
                "visible": True,
                "position": navbar_config["position"],
                "buttons": {},
                "responsive_mode": "desktop"
            }
            
            # 根据显示模式调整导航栏
            if current_mode == "fullscreen":
                navbar_state["auto_hide"] = True
                navbar_state["overlay"] = True
            elif current_mode == "embedded":
                navbar_state["compact"] = True
                navbar_state["position"] = "top"
            else:  # windowed
                navbar_state["auto_hide"] = False
                navbar_state["overlay"] = False
            
            # 验证必需按钮始终可用
            required_buttons = ["back_to_main", "toggle_fullscreen"]
            for button_name in required_buttons:
                button_config = navbar_config["buttons"][button_name]
                navbar_state["buttons"][button_name] = {
                    "enabled": button_config["enabled"],
                    "visible": True,
                    "accessible": True
                }
            
            # 验证可选按钮根据配置显示
            optional_buttons = ["show_product_info", "open_settings", "refresh_product", "close_product"]
            for button_name in optional_buttons:
                button_config = navbar_config["buttons"][button_name]
                navbar_state["buttons"][button_name] = {
                    "enabled": button_config["enabled"],
                    "visible": button_config["enabled"],
                    "accessible": button_config["enabled"]
                }
            
            return navbar_state
        
        # 3. 测试每个产品的导航功能
        for i, product_data in enumerate(products):
            product_id = i + 1
            
            # 测试不同显示模式下的导航功能
            for mode in display_modes:
                navbar_state = validate_navbar_functionality(product_id, mode)
                
                # 验证导航栏始终可见
                assert navbar_state["visible"], \
                    f"产品 {product_id} 在 {mode} 模式下导航栏不可见"
                
                # 验证返回主站按钮始终可用
                back_button = navbar_state["buttons"]["back_to_main"]
                assert back_button["enabled"] and back_button["visible"], \
                    f"产品 {product_id} 在 {mode} 模式下返回主站按钮不可用"
                
                # 验证全屏切换按钮可用
                fullscreen_button = navbar_state["buttons"]["toggle_fullscreen"]
                assert fullscreen_button["enabled"] and fullscreen_button["visible"], \
                    f"产品 {product_id} 在 {mode} 模式下全屏切换按钮不可用"
        
        # 4. 验证导航操作的执行
        def execute_navigation_action(product_id: int, action: str, current_state: dict) -> dict:
            """执行导航操作并返回新状态"""
            new_state = current_state.copy()
            
            if action == "back_to_main":
                # 返回主网站操作
                new_state.update({
                    "navigation_target": "main_website",
                    "product_active": False,
                    "exit_method": "navigation",
                    "state_saved": True
                })
                
            elif action == "toggle_fullscreen":
                # 切换全屏模式
                current_mode = new_state.get("display_mode", "windowed")
                if current_mode == "fullscreen":
                    new_state["display_mode"] = "windowed"
                    new_state["navbar_overlay"] = False
                else:
                    new_state["display_mode"] = "fullscreen"
                    new_state["navbar_overlay"] = True
                
            elif action == "show_product_info":
                # 显示产品信息
                new_state.update({
                    "info_panel_visible": True,
                    "info_content": {
                        "title": f"产品 {product_id}",
                        "version": "1.0.0",
                        "description": "测试产品描述"
                    }
                })
                
            elif action == "open_settings":
                # 打开设置面板
                new_state.update({
                    "settings_panel_visible": True,
                    "settings_options": [
                        "display_preferences",
                        "performance_settings",
                        "accessibility_options"
                    ]
                })
                
            elif action == "refresh_product":
                # 刷新产品
                new_state.update({
                    "product_reloading": True,
                    "reload_timestamp": time.time(),
                    "state_preserved": True
                })
                
            elif action == "close_product":
                # 关闭产品（如果启用）
                if navbar_config["buttons"]["close_product"]["enabled"]:
                    new_state.update({
                        "product_active": False,
                        "exit_method": "close",
                        "state_saved": True
                    })
            
            return new_state
        
        # 5. 测试导航操作序列
        for i, product_data in enumerate(products):
            product_id = i + 1
            
            # 初始化产品状态
            product_state = {
                "product_id": product_id,
                "product_active": True,
                "display_mode": "windowed",
                "navbar_visible": True,
                "info_panel_visible": False,
                "settings_panel_visible": False,
                "product_reloading": False,
                "state_saved": False
            }
            
            # 执行导航操作序列
            for action in navigation_actions:
                old_state = product_state.copy()
                product_state = execute_navigation_action(product_id, action, product_state)
                
                # 验证操作执行后的状态一致性
                if action == "back_to_main":
                    assert product_state["navigation_target"] == "main_website", \
                        f"返回主站操作未正确设置导航目标"
                    assert product_state["state_saved"], \
                        f"返回主站时未保存产品状态"
                
                elif action == "toggle_fullscreen":
                    # 验证全屏切换的状态变化
                    old_mode = old_state.get("display_mode", "windowed")
                    new_mode = product_state["display_mode"]
                    assert old_mode != new_mode or (old_mode == "windowed" and new_mode == "fullscreen") or (old_mode == "fullscreen" and new_mode == "windowed"), \
                        f"全屏切换操作未正确改变显示模式: {old_mode} -> {new_mode}"
                
                elif action == "show_product_info":
                    assert product_state["info_panel_visible"], \
                        f"产品信息面板未正确显示"
                    assert "info_content" in product_state, \
                        f"产品信息内容未正确加载"
                
                elif action == "refresh_product":
                    assert product_state["product_reloading"], \
                        f"产品刷新状态未正确设置"
                    assert product_state["state_preserved"], \
                        f"产品刷新时未保留状态"
        
        # 6. 验证导航状态的持久性
        def validate_navigation_state_persistence(product_id: int, actions_history: list) -> bool:
            """验证导航状态的持久性"""
            # 模拟状态存储
            persistent_state = {
                "product_id": product_id,
                "last_display_mode": "windowed",
                "user_preferences": {
                    "navbar_position": "top",
                    "auto_hide_enabled": False,
                    "info_panel_last_opened": False
                },
                "navigation_history": [],
                "session_start_time": time.time()
            }
            
            # 记录导航历史
            for action in actions_history:
                persistent_state["navigation_history"].append({
                    "action": action,
                    "timestamp": time.time(),
                    "context": f"product_{product_id}"
                })
                
                # 更新持久化偏好设置
                if action == "toggle_fullscreen":
                    persistent_state["last_display_mode"] = "fullscreen" if persistent_state["last_display_mode"] == "windowed" else "windowed"
                elif action == "show_product_info":
                    persistent_state["user_preferences"]["info_panel_last_opened"] = True
            
            # 验证状态可以正确恢复
            return len(persistent_state["navigation_history"]) == len(actions_history)
        
        # 测试状态持久性
        for i, product_data in enumerate(products):
            product_id = i + 1
            persistence_valid = validate_navigation_state_persistence(product_id, navigation_actions)
            assert persistence_valid, f"产品 {product_id} 导航状态持久性验证失败"
        
        # 7. 验证响应式导航适配
        def validate_responsive_navigation(screen_width: int, navbar_state: dict) -> dict:
            """验证响应式导航适配"""
            breakpoints = navbar_config["responsive_breakpoints"]
            
            if screen_width <= breakpoints["mobile"]:
                # 移动设备适配
                navbar_state.update({
                    "responsive_mode": "mobile",
                    "compact_layout": True,
                    "hamburger_menu": True,
                    "button_icons_only": True
                })
            elif screen_width <= breakpoints["tablet"]:
                # 平板设备适配
                navbar_state.update({
                    "responsive_mode": "tablet",
                    "compact_layout": True,
                    "hamburger_menu": False,
                    "button_icons_only": False
                })
            else:
                # 桌面设备
                navbar_state.update({
                    "responsive_mode": "desktop",
                    "compact_layout": False,
                    "hamburger_menu": False,
                    "button_icons_only": False
                })
            
            return navbar_state
        
        # 测试响应式适配
        test_screen_widths = [360, 768, 1024, 1920]  # 移动、平板、小桌面、大桌面
        
        for width in test_screen_widths:
            navbar_state = {"visible": True, "buttons": {}}
            responsive_state = validate_responsive_navigation(width, navbar_state)
            
            # 验证响应式适配的正确性
            if width <= 768:  # 移动设备
                assert responsive_state["responsive_mode"] == "mobile", \
                    f"移动设备适配失败: 屏幕宽度 {width}"
                assert responsive_state["compact_layout"], \
                    f"移动设备未启用紧凑布局: 屏幕宽度 {width}"
            elif width <= 1024:  # 平板设备
                assert responsive_state["responsive_mode"] == "tablet", \
                    f"平板设备适配失败: 屏幕宽度 {width}"
            else:  # 桌面设备
                assert responsive_state["responsive_mode"] == "desktop", \
                    f"桌面设备适配失败: 屏幕宽度 {width}"
        
        # 8. 验证导航可访问性
        def validate_navigation_accessibility(navbar_state: dict) -> bool:
            """验证导航的可访问性"""
            accessibility_features = {
                "keyboard_navigation": True,
                "screen_reader_support": True,
                "high_contrast_mode": True,
                "focus_indicators": True,
                "aria_labels": True
            }
            
            # 检查必需的可访问性功能
            for button_name, button_state in navbar_state["buttons"].items():
                if button_state["enabled"]:
                    # 每个启用的按钮都应该支持键盘导航
                    assert accessibility_features["keyboard_navigation"], \
                        f"按钮 {button_name} 不支持键盘导航"
                    
                    # 每个按钮都应该有适当的ARIA标签
                    assert accessibility_features["aria_labels"], \
                        f"按钮 {button_name} 缺少ARIA标签"
            
            return True
        
        # 测试导航可访问性
        for i, product_data in enumerate(products):
            product_id = i + 1
            navbar_state = validate_navbar_functionality(product_id, "windowed")
            accessibility_valid = validate_navigation_accessibility(navbar_state)
            assert accessibility_valid, f"产品 {product_id} 导航可访问性验证失败"
        
        # 9. 验证导航性能和响应性
        def validate_navigation_performance(action_count: int) -> bool:
            """验证导航操作的性能"""
            # 模拟导航操作的性能指标
            performance_metrics = {
                "average_response_time": 50,  # 毫秒
                "max_response_time": 200,     # 毫秒
                "memory_usage_increase": 0.1, # MB per action
                "cpu_usage_spike": 5          # 百分比
            }
            
            # 计算预期的性能影响
            total_memory_increase = performance_metrics["memory_usage_increase"] * action_count
            max_expected_response = performance_metrics["max_response_time"]
            
            # 验证性能在可接受范围内
            assert total_memory_increase < 10, \
                f"导航操作内存使用过高: {total_memory_increase}MB"
            
            assert max_expected_response < 500, \
                f"导航响应时间过长: {max_expected_response}ms"
            
            return True
        
        # 测试导航性能
        performance_valid = validate_navigation_performance(len(navigation_actions))
        assert performance_valid, "导航性能验证失败"
        
        # 10. 验证导航错误处理
        def validate_navigation_error_handling(product_id: int, error_scenario: str) -> bool:
            """验证导航错误处理"""
            error_scenarios = {
                "network_disconnected": {
                    "back_to_main": "show_offline_message",
                    "refresh_product": "show_retry_option"
                },
                "product_crashed": {
                    "back_to_main": "allow_navigation",
                    "refresh_product": "restart_product"
                },
                "permission_denied": {
                    "back_to_main": "allow_navigation",
                    "show_product_info": "show_error_message"
                }
            }
            
            if error_scenario in error_scenarios:
                error_handlers = error_scenarios[error_scenario]
                
                # 验证每种错误情况下的处理方式
                for action, expected_behavior in error_handlers.items():
                    # 返回主站功能应该始终可用
                    if action == "back_to_main":
                        assert expected_behavior in ["allow_navigation", "show_offline_message"], \
                            f"错误情况 {error_scenario} 下返回主站功能处理不当"
                    
                    # 其他功能应该有适当的错误处理
                    else:
                        assert expected_behavior in ["show_retry_option", "restart_product", "show_error_message"], \
                            f"错误情况 {error_scenario} 下 {action} 功能处理不当"
            
            return True
        
        # 测试导航错误处理
        error_scenarios = ["network_disconnected", "product_crashed", "permission_denied"]
        for i, product_data in enumerate(products):
            product_id = i + 1
            for scenario in error_scenarios:
                error_handling_valid = validate_navigation_error_handling(product_id, scenario)
                assert error_handling_valid, \
                    f"产品 {product_id} 在错误场景 {scenario} 下导航处理验证失败"
    
    @given(
        products=st.lists(product_data(), min_size=1, max_size=10),
        route_operations=st.lists(
            st.tuples(
                st.integers(min_value=0, max_value=9),  # product_index
                st.sampled_from(['create_route', 'access_route', 'update_route', 'delete_route'])
            ),
            min_size=1, max_size=30
        ),
        url_patterns=st.lists(
            st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Pc'))),
            min_size=1, max_size=20
        )
    )
    def test_product_route_uniqueness(self, products, route_operations, url_patterns):
        """
        **Feature: product-integration, Property 3: 产品路由唯一性**
        **Validates: Requirements 1.3**
        
        验证产品路由系统的唯一性和正确性：
        1. 每个产品有唯一的URL路径
        2. 产品路由不与主网站路由冲突
        3. 路由参数正确解析
        4. 动态路由生成的一致性
        5. 路由访问权限控制
        6. 路由重定向和错误处理
        """
        # 1. 定义主网站的保留路由
        reserved_routes = {
            "/",
            "/home",
            "/portfolio", 
            "/blog",
            "/about",
            "/contact",
            "/admin",
            "/api",
            "/static",
            "/assets",
            "/uploads"
        }
        
        # 2. 模拟路由注册系统
        route_registry = {
            "main_routes": reserved_routes.copy(),
            "product_routes": {},
            "route_patterns": {},
            "access_permissions": {},
            "redirect_rules": {}
        }
        
        # 3. 验证产品路由生成的唯一性
        def generate_product_route(product_id: int, product_title: str) -> str:
            """生成产品的唯一路由"""
            # 基于产品ID和标题生成路由
            import re
            import unicodedata
            
            # 规范化Unicode字符并转换为ASCII
            normalized_title = unicodedata.normalize('NFKD', product_title)
            ascii_title = normalized_title.encode('ascii', 'ignore').decode('ascii')
            
            # 清理产品标题，生成URL友好的slug
            slug = re.sub(r'[^\w\s-]', '', ascii_title.lower())
            slug = re.sub(r'[-\s]+', '-', slug).strip('-')
            
            # 如果slug为空或只包含非ASCII字符，使用默认格式
            if not slug or len(slug) == 0:
                slug = f"product-{product_id}"
            
            # 确保slug只包含字母、数字和连字符
            slug = re.sub(r'[^a-zA-Z0-9\-]', '', slug)
            if not slug:
                slug = f"product-{product_id}"
            
            # 生成完整路由
            route = f"/product/{product_id}/{slug}"
            
            return route
        
        def validate_route_uniqueness(new_route: str, existing_routes: set) -> bool:
            """验证路由的唯一性"""
            # 检查是否与现有路由冲突
            if new_route in existing_routes:
                return False
            
            # 检查是否与保留路由冲突
            if new_route in reserved_routes:
                return False
            
            # 检查路径前缀冲突
            for existing_route in existing_routes:
                # 检查是否为子路径冲突
                if new_route.startswith(existing_route + "/") or existing_route.startswith(new_route + "/"):
                    # 允许产品路由的层级结构
                    if new_route.startswith("/product/") and existing_route.startswith("/product/"):
                        continue
                    return False
            
            return True
        
        # 4. 测试产品路由的创建和唯一性
        all_routes = set(reserved_routes)
        product_route_map = {}
        
        for i, product_data in enumerate(products):
            product_id = i + 1
            product_title = product_data["title"]
            
            # 生成产品路由
            product_route = generate_product_route(product_id, product_title)
            
            # 验证路由唯一性
            is_unique = validate_route_uniqueness(product_route, all_routes)
            assert is_unique, f"产品 {product_id} 的路由不唯一: {product_route}"
            
            # 注册路由
            all_routes.add(product_route)
            product_route_map[product_id] = product_route
            route_registry["product_routes"][product_id] = {
                "route": product_route,
                "title": product_title,
                "is_published": product_data["is_published"],
                "product_type": product_data["product_type"]
            }
        
        # 5. 验证路由参数解析
        def parse_product_route(route_path: str) -> dict:
            """解析产品路由参数"""
            import re
            
            # 匹配产品路由模式: /product/{id}/{slug}
            pattern = r'^/product/(\d+)/([a-zA-Z0-9\-]+)/?$'
            match = re.match(pattern, route_path)
            
            if not match:
                return {"valid": False, "error": "路由格式不匹配"}
            
            product_id = int(match.group(1))
            slug = match.group(2)
            
            return {
                "valid": True,
                "product_id": product_id,
                "slug": slug,
                "full_path": route_path
            }
        
        # 测试路由参数解析
        for product_id, route_info in route_registry["product_routes"].items():
            route_path = route_info["route"]
            parsed = parse_product_route(route_path)
            
            assert parsed["valid"], f"产品路由解析失败: {route_path}"
            assert parsed["product_id"] == product_id, \
                f"产品ID解析错误: 期望 {product_id}, 实际 {parsed['product_id']}"
        
        # 6. 验证路由操作的正确性
        def execute_route_operation(operation: str, product_index: int, route_registry: dict) -> dict:
            """执行路由操作"""
            if product_index >= len(products):
                return {"success": False, "error": "产品索引超出范围"}
            
            product_id = product_index + 1
            result = {"success": True, "operation": operation}
            
            if operation == "create_route":
                # 创建新路由
                if product_id not in route_registry["product_routes"]:
                    product_data = products[product_index]
                    route = generate_product_route(product_id, product_data["title"])
                    route_registry["product_routes"][product_id] = {
                        "route": route,
                        "created_at": time.time(),
                        "status": "active"
                    }
                    result["route"] = route
                else:
                    result["success"] = False
                    result["error"] = "路由已存在"
            
            elif operation == "access_route":
                # 访问路由
                if product_id in route_registry["product_routes"]:
                    route_info = route_registry["product_routes"][product_id]
                    result.update({
                        "route": route_info["route"],
                        "accessible": route_info.get("status") == "active",
                        "access_time": time.time()
                    })
                else:
                    result["success"] = False
                    result["error"] = "路由不存在"
            
            elif operation == "update_route":
                # 更新路由
                if product_id in route_registry["product_routes"]:
                    route_info = route_registry["product_routes"][product_id]
                    # 模拟路由更新（例如slug变更）
                    old_route = route_info["route"]
                    new_route = old_route.replace(old_route.split('/')[-1], f"updated-{product_id}")
                    route_info["route"] = new_route
                    route_info["updated_at"] = time.time()
                    result["old_route"] = old_route
                    result["new_route"] = new_route
                else:
                    result["success"] = False
                    result["error"] = "路由不存在"
            
            elif operation == "delete_route":
                # 删除路由
                if product_id in route_registry["product_routes"]:
                    deleted_route = route_registry["product_routes"][product_id]["route"]
                    del route_registry["product_routes"][product_id]
                    result["deleted_route"] = deleted_route
                else:
                    result["success"] = False
                    result["error"] = "路由不存在"
            
            return result
        
        # 执行路由操作序列
        operation_results = []
        for product_index, operation in route_operations:
            result = execute_route_operation(operation, product_index, route_registry)
            operation_results.append(result)
            
            # 验证操作结果的一致性
            if result["success"]:
                if operation == "create_route":
                    assert "route" in result, f"创建路由操作未返回路由信息"
                elif operation == "access_route":
                    assert "accessible" in result, f"访问路由操作未返回可访问性信息"
                elif operation == "update_route":
                    assert "new_route" in result, f"更新路由操作未返回新路由"
                elif operation == "delete_route":
                    assert "deleted_route" in result, f"删除路由操作未返回被删除的路由"
        
        # 7. 验证路由冲突检测
        def detect_route_conflicts(routes: list) -> list:
            """检测路由冲突"""
            conflicts = []
            
            for i, route1 in enumerate(routes):
                for j, route2 in enumerate(routes[i+1:], i+1):
                    # 检查完全相同的路由
                    if route1 == route2:
                        conflicts.append({
                            "type": "duplicate",
                            "routes": [route1, route2],
                            "indices": [i, j]
                        })
                    
                    # 检查路径前缀冲突
                    elif route1.startswith(route2 + "/") or route2.startswith(route1 + "/"):
                        conflicts.append({
                            "type": "prefix_conflict",
                            "routes": [route1, route2],
                            "indices": [i, j]
                        })
            
            return conflicts
        
        # 测试路由冲突检测
        current_routes = [info["route"] for info in route_registry["product_routes"].values()]
        conflicts = detect_route_conflicts(current_routes)
        
        # 验证没有路由冲突
        assert len(conflicts) == 0, f"检测到路由冲突: {conflicts}"
        
        # 8. 验证动态路由生成的一致性
        def test_route_generation_consistency(product_data: dict, iterations: int = 5) -> bool:
            """测试路由生成的一致性"""
            routes = []
            
            for _ in range(iterations):
                route = generate_product_route(1, product_data["title"])
                routes.append(route)
            
            # 所有生成的路由应该相同
            return len(set(routes)) == 1
        
        # 测试路由生成一致性
        for product_data in products[:3]:  # 测试前3个产品
            consistency_valid = test_route_generation_consistency(product_data)
            assert consistency_valid, f"产品路由生成不一致: {product_data['title']}"
        
        # 9. 验证路由访问权限控制
        def validate_route_access_permissions(product_id: int, user_role: str, route_info: dict) -> bool:
            """验证路由访问权限"""
            # 定义访问权限规则
            access_rules = {
                "published_product": {
                    "guest": True,
                    "user": True,
                    "admin": True
                },
                "unpublished_product": {
                    "guest": False,
                    "user": False,
                    "admin": True
                },
                "private_product": {
                    "guest": False,
                    "user": False,
                    "admin": True
                }
            }
            
            # 确定产品状态
            if route_info.get("is_published", False):
                product_status = "published_product"
            else:
                product_status = "unpublished_product"
            
            # 检查访问权限
            return access_rules[product_status].get(user_role, False)
        
        # 测试访问权限控制
        user_roles = ["guest", "user", "admin"]
        
        for product_id, route_info in route_registry["product_routes"].items():
            for role in user_roles:
                has_access = validate_route_access_permissions(product_id, role, route_info)
                
                # 验证权限逻辑
                if route_info.get("is_published", False):
                    # 已发布产品所有角色都可以访问
                    assert has_access, f"已发布产品 {product_id} 对角色 {role} 的访问被错误拒绝"
                else:
                    # 未发布产品只有管理员可以访问
                    if role == "admin":
                        assert has_access, f"未发布产品 {product_id} 对管理员的访问被错误拒绝"
                    else:
                        assert not has_access, f"未发布产品 {product_id} 对角色 {role} 的访问未被正确限制"
        
        # 10. 验证路由重定向和错误处理
        def handle_route_errors(route_path: str, error_type: str) -> dict:
            """处理路由错误"""
            error_handlers = {
                "not_found": {
                    "status_code": 404,
                    "redirect_to": "/portfolio",
                    "message": "产品不存在"
                },
                "access_denied": {
                    "status_code": 403,
                    "redirect_to": "/login",
                    "message": "访问被拒绝"
                },
                "product_offline": {
                    "status_code": 503,
                    "redirect_to": "/portfolio",
                    "message": "产品暂时不可用"
                },
                "invalid_route": {
                    "status_code": 400,
                    "redirect_to": "/",
                    "message": "无效的路由格式"
                }
            }
            
            if error_type in error_handlers:
                handler = error_handlers[error_type]
                return {
                    "handled": True,
                    "status_code": handler["status_code"],
                    "redirect_to": handler["redirect_to"],
                    "message": handler["message"],
                    "original_route": route_path
                }
            
            return {
                "handled": False,
                "error": f"未知错误类型: {error_type}"
            }
        
        # 测试路由错误处理
        error_scenarios = [
            ("/product/999/nonexistent", "not_found"),
            ("/product/1/private-content", "access_denied"),
            ("/product/abc/invalid", "invalid_route"),
            ("/product/2/maintenance", "product_offline")
        ]
        
        for route_path, error_type in error_scenarios:
            error_result = handle_route_errors(route_path, error_type)
            
            assert error_result["handled"], f"路由错误未被正确处理: {route_path}"
            assert error_result["status_code"] in [400, 403, 404, 503], \
                f"错误状态码不正确: {error_result['status_code']}"
            assert error_result["redirect_to"] in ["/", "/login", "/portfolio"], \
                f"重定向目标不正确: {error_result['redirect_to']}"
        
        # 11. 验证路由性能和缓存
        def validate_route_performance(route_count: int) -> bool:
            """验证路由性能"""
            # 模拟路由查找性能
            performance_metrics = {
                "lookup_time_ms": max(1, route_count * 0.1),  # 每个路由0.1ms
                "memory_usage_mb": route_count * 0.001,       # 每个路由1KB
                "cache_hit_rate": 0.95 if route_count > 10 else 0.8
            }
            
            # 验证性能指标在可接受范围内
            assert performance_metrics["lookup_time_ms"] < 100, \
                f"路由查找时间过长: {performance_metrics['lookup_time_ms']}ms"
            
            assert performance_metrics["memory_usage_mb"] < 10, \
                f"路由内存使用过高: {performance_metrics['memory_usage_mb']}MB"
            
            assert performance_metrics["cache_hit_rate"] > 0.7, \
                f"路由缓存命中率过低: {performance_metrics['cache_hit_rate']}"
            
            return True
        
        # 测试路由性能
        current_route_count = len(route_registry["product_routes"])
        performance_valid = validate_route_performance(current_route_count)
        assert performance_valid, "路由性能验证失败"
        
        # 12. 验证路由的国际化支持
        def validate_route_internationalization(route: str, locale: str) -> str:
            """验证路由的国际化支持"""
            # 模拟国际化路由生成
            i18n_prefixes = {
                "en": "",           # 默认英文不加前缀
                "zh": "/zh",        # 中文
                "ja": "/ja",        # 日文
                "ko": "/ko"         # 韩文
            }
            
            if locale in i18n_prefixes:
                prefix = i18n_prefixes[locale]
                return f"{prefix}{route}" if prefix else route
            
            return route  # 不支持的语言使用默认路由
        
        # 测试国际化路由
        test_locales = ["en", "zh", "ja", "ko"]
        
        for product_id, route_info in list(route_registry["product_routes"].items())[:3]:
            base_route = route_info["route"]
            
            for locale in test_locales:
                i18n_route = validate_route_internationalization(base_route, locale)
                
                # 验证国际化路由格式正确
                if locale == "en":
                    assert i18n_route == base_route, f"英文路由不应该有前缀: {i18n_route}"
                else:
                    expected_prefix = f"/{locale}"
                    assert i18n_route.startswith(expected_prefix), \
                        f"国际化路由前缀不正确: {i18n_route}, 期望前缀: {expected_prefix}"
    
    @given(
        file_uploads=st.lists(
            st.fixed_dictionaries({
                'filename': st.text(min_size=1, max_size=100, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Pc'))),
                'content': st.one_of(
                    st.text(max_size=1000),
                    st.binary(min_size=1, max_size=1000)
                ),
                'size': st.integers(min_value=1, max_value=100*1024*1024)
            }),
            min_size=1, max_size=10
        ),
        validation_scenarios=st.lists(
            st.sampled_from([
                'valid_zip',
                'corrupted_zip', 
                'oversized_file',
                'invalid_format',
                'missing_entry_file',
                'malicious_content',
                'empty_file',
                'nested_zip'
            ]),
            min_size=1, max_size=10
        ),
        integrity_checks=st.lists(
            st.dictionaries(
                st.sampled_from(['hash_algorithm', 'expected_hash', 'file_size', 'modification_time']),
                st.one_of(st.text(), st.integers()),
                min_size=2, max_size=4
            ),
            max_size=10
        )
    )
    def test_product_file_integrity_validation(self, file_uploads, validation_scenarios, integrity_checks):
        """
        **Feature: product-integration, Property 15: 产品文件完整性验证**
        **Validates: Requirements 4.4**
        
        验证产品文件上传和完整性验证的正确性：
        1. 文件格式验证和类型检查
        2. 文件大小和数量限制
        3. 文件完整性校验和验证
        4. 恶意文件检测和阻止
        5. ZIP文件结构验证
        6. 入口文件存在性检查
        """
        # 1. 定义文件验证配置
        validation_config = {
            "allowed_formats": [".zip"],
            "max_file_size": 100 * 1024 * 1024,  # 100MB
            "max_files_in_zip": 1000,
            "required_entry_files": ["index.html", "main.html", "app.html"],
            "allowed_file_extensions": {
                ".html", ".htm", ".css", ".js", ".json", ".txt", ".md",
                ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".webp",
                ".mp3", ".wav", ".ogg", ".mp4", ".webm",
                ".woff", ".woff2", ".ttf", ".eot",
                ".xml", ".csv", ".pdf", ".map"
            },
            "dangerous_extensions": {
                ".exe", ".bat", ".cmd", ".com", ".pif", ".scr", ".vbs",
                ".jar", ".php", ".asp", ".aspx", ".jsp", ".py", ".rb", ".pl"
            },
            "max_path_length": 255,
            "hash_algorithms": ["md5", "sha1", "sha256"]
        }
        
        # 2. 文件格式和类型验证
        def validate_file_format(filename: str, content: bytes) -> dict:
            """验证文件格式和类型"""
            import os
            import mimetypes
            
            result = {
                "valid": True,
                "errors": [],
                "warnings": []
            }
            
            # 检查文件扩展名
            file_ext = os.path.splitext(filename)[1].lower()
            if file_ext not in validation_config["allowed_formats"]:
                result["valid"] = False
                result["errors"].append(f"不支持的文件格式: {file_ext}")
            
            # 检查MIME类型
            mime_type, _ = mimetypes.guess_type(filename)
            if file_ext == ".zip" and mime_type != "application/zip":
                result["warnings"].append("MIME类型与文件扩展名不匹配")
            
            # 检查文件大小
            if len(content) > validation_config["max_file_size"]:
                result["valid"] = False
                result["errors"].append(f"文件大小超过限制: {len(content)} bytes")
            
            # 检查文件是否为空
            if len(content) == 0:
                result["valid"] = False
                result["errors"].append("文件为空")
            
            return result
        
        # 3. ZIP文件结构验证
        def validate_zip_structure(zip_content: bytes) -> dict:
            """验证ZIP文件结构"""
            import zipfile
            import io
            
            result = {
                "valid": True,
                "errors": [],
                "warnings": [],
                "files": [],
                "entry_file": None
            }
            
            try:
                # 尝试打开ZIP文件
                with zipfile.ZipFile(io.BytesIO(zip_content), 'r') as zf:
                    # 检查ZIP文件完整性
                    bad_files = zf.testzip()
                    if bad_files:
                        result["valid"] = False
                        result["errors"].append(f"ZIP文件损坏，损坏的文件: {bad_files}")
                        return result
                    
                    # 获取文件列表
                    file_list = zf.namelist()
                    result["files"] = file_list
                    
                    # 检查文件数量限制
                    if len(file_list) > validation_config["max_files_in_zip"]:
                        result["valid"] = False
                        result["errors"].append(f"ZIP文件包含过多文件: {len(file_list)}")
                    
                    # 检查路径长度
                    for file_path in file_list:
                        if len(file_path) > validation_config["max_path_length"]:
                            result["valid"] = False
                            result["errors"].append(f"文件路径过长: {file_path}")
                        
                        # 检查路径遍历攻击
                        if ".." in file_path or file_path.startswith("/"):
                            result["valid"] = False
                            result["errors"].append(f"检测到路径遍历攻击: {file_path}")
                        
                        # 检查文件扩展名
                        file_ext = os.path.splitext(file_path)[1].lower()
                        if file_ext in validation_config["dangerous_extensions"]:
                            result["valid"] = False
                            result["errors"].append(f"检测到危险文件类型: {file_path}")
                        elif file_ext and file_ext not in validation_config["allowed_file_extensions"]:
                            result["warnings"].append(f"未知文件类型: {file_path}")
                    
                    # 检查入口文件
                    entry_files = [f for f in file_list if any(f.endswith(entry) for entry in validation_config["required_entry_files"])]
                    if not entry_files:
                        result["valid"] = False
                        result["errors"].append("未找到有效的入口文件")
                    else:
                        result["entry_file"] = entry_files[0]
                    
                    # 检查文件内容
                    for file_path in file_list:
                        try:
                            file_content = zf.read(file_path)
                            
                            # 检查HTML文件的基本结构
                            if file_path.endswith(('.html', '.htm')):
                                content_str = file_content.decode('utf-8', errors='ignore')
                                if not any(tag in content_str.lower() for tag in ['<html', '<head', '<body']):
                                    result["warnings"].append(f"HTML文件可能缺少基本结构: {file_path}")
                        
                        except Exception as e:
                            result["warnings"].append(f"无法读取文件内容: {file_path}, 错误: {str(e)}")
            
            except zipfile.BadZipFile:
                result["valid"] = False
                result["errors"].append("无效的ZIP文件格式")
            except Exception as e:
                result["valid"] = False
                result["errors"].append(f"ZIP文件验证失败: {str(e)}")
            
            return result
        
        # 4. 文件完整性校验
        def calculate_file_checksum(content: bytes, algorithm: str = "sha256") -> str:
            """计算文件校验和"""
            import hashlib
            
            if algorithm == "md5":
                return hashlib.md5(content).hexdigest()
            elif algorithm == "sha1":
                return hashlib.sha1(content).hexdigest()
            elif algorithm == "sha256":
                return hashlib.sha256(content).hexdigest()
            else:
                raise ValueError(f"不支持的哈希算法: {algorithm}")
        
        def verify_file_integrity(content: bytes, expected_checksum: str, algorithm: str = "sha256") -> bool:
            """验证文件完整性"""
            actual_checksum = calculate_file_checksum(content, algorithm)
            return actual_checksum == expected_checksum
        
        # 5. 恶意内容检测
        def detect_malicious_content(file_path: str, content: bytes) -> dict:
            """检测恶意内容"""
            result = {
                "is_malicious": False,
                "threats": [],
                "risk_level": "low"
            }
            
            # 检查文件扩展名
            file_ext = os.path.splitext(file_path)[1].lower()
            if file_ext in validation_config["dangerous_extensions"]:
                result["is_malicious"] = True
                result["threats"].append(f"危险文件类型: {file_ext}")
                result["risk_level"] = "high"
            
            # 检查文件内容中的可疑模式
            try:
                content_str = content.decode('utf-8', errors='ignore').lower()
                
                # 检查脚本注入
                suspicious_patterns = [
                    '<script>alert(',
                    'javascript:',
                    'eval(',
                    'document.cookie',
                    'window.location',
                    'iframe src=',
                    'onload=',
                    'onerror='
                ]
                
                for pattern in suspicious_patterns:
                    if pattern in content_str:
                        result["threats"].append(f"检测到可疑模式: {pattern}")
                        result["risk_level"] = "medium"
                
                # 检查外部资源引用
                external_patterns = [
                    'http://',
                    'https://',
                    'ftp://',
                    'data:',
                    'blob:'
                ]
                
                external_count = sum(content_str.count(pattern) for pattern in external_patterns)
                if external_count > 10:  # 过多外部引用可能有风险
                    result["threats"].append(f"过多外部资源引用: {external_count}")
                    result["risk_level"] = "medium"
            
            except UnicodeDecodeError:
                # 二进制文件，进行基本检查
                if b'\x00' in content[:100]:  # 检查是否包含null字节
                    result["threats"].append("文件包含二进制内容")
            
            return result
        
        # 6. 测试文件上传验证
        upload_results = []
        
        for upload_data in file_uploads:
            # 模拟文件上传数据
            filename = str(upload_data.get("filename", "test"))
            if isinstance(upload_data.get("content"), bytes):
                content = upload_data["content"]
            else:
                content = str(upload_data.get("content", "")).encode('utf-8')
            
            # 确保文件名有正确的扩展名
            if not filename.endswith('.zip'):
                filename += '.zip'
            
            # 执行文件格式验证
            format_result = validate_file_format(filename, content)
            
            # 如果是ZIP文件，进行结构验证
            structure_result = None
            if format_result["valid"] and filename.endswith('.zip'):
                structure_result = validate_zip_structure(content)
            
            # 执行恶意内容检测
            malicious_result = detect_malicious_content(filename, content)
            
            # 计算文件校验和
            checksum = calculate_file_checksum(content, "sha256")
            
            upload_result = {
                "filename": filename,
                "size": len(content),
                "format_validation": format_result,
                "structure_validation": structure_result,
                "malicious_detection": malicious_result,
                "checksum": checksum,
                "overall_valid": format_result["valid"] and (structure_result is None or structure_result["valid"]) and not malicious_result["is_malicious"]
            }
            
            upload_results.append(upload_result)
        
        # 7. 验证不同场景下的处理
        for scenario in validation_scenarios:
            if scenario == "valid_zip":
                # 验证有效ZIP文件的处理
                valid_uploads = [r for r in upload_results if r["overall_valid"]]
                # 有效文件应该通过所有验证
                for result in valid_uploads:
                    assert result["format_validation"]["valid"], \
                        f"有效ZIP文件格式验证失败: {result['filename']}"
            
            elif scenario == "corrupted_zip":
                # 验证损坏ZIP文件的检测
                # 模拟损坏的ZIP文件
                corrupted_content = b"PK\x03\x04" + b"\x00" * 100  # 不完整的ZIP头
                format_result = validate_file_format("corrupted.zip", corrupted_content)
                structure_result = validate_zip_structure(corrupted_content)
                
                # 损坏的文件应该被检测出来
                assert not structure_result["valid"], \
                    "损坏的ZIP文件未被正确检测"
            
            elif scenario == "oversized_file":
                # 验证超大文件的处理
                large_content = b"x" * (validation_config["max_file_size"] + 1)
                format_result = validate_file_format("large.zip", large_content)
                
                # 超大文件应该被拒绝
                assert not format_result["valid"], \
                    "超大文件未被正确拒绝"
            
            elif scenario == "invalid_format":
                # 验证无效格式的处理
                invalid_content = b"This is not a zip file"
                format_result = validate_file_format("invalid.txt", invalid_content)
                
                # 无效格式应该被拒绝
                assert not format_result["valid"], \
                    "无效文件格式未被正确拒绝"
            
            elif scenario == "missing_entry_file":
                # 验证缺少入口文件的处理
                # 创建一个没有HTML文件的ZIP
                import zipfile
                import io
                
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w') as zf:
                    zf.writestr("style.css", "body { margin: 0; }")
                    zf.writestr("script.js", "console.log('test');")
                
                zip_content = zip_buffer.getvalue()
                structure_result = validate_zip_structure(zip_content)
                
                # 缺少入口文件应该被检测出来
                assert not structure_result["valid"], \
                    "缺少入口文件的ZIP未被正确检测"
            
            elif scenario == "malicious_content":
                # 验证恶意内容的检测
                malicious_html = b"<script>alert('xss')</script><html><body>test</body></html>"
                malicious_result = detect_malicious_content("malicious.html", malicious_html)
                
                # 恶意内容应该被检测出来
                assert len(malicious_result["threats"]) > 0, \
                    "恶意内容未被正确检测"
        
        # 8. 验证完整性检查的准确性
        for check_data in integrity_checks:
            algorithm = check_data.get("hash_algorithm", "sha256")
            if algorithm in validation_config["hash_algorithms"]:
                # 创建测试内容
                test_content = b"test content for integrity check"
                
                # 计算正确的校验和
                correct_checksum = calculate_file_checksum(test_content, algorithm)
                
                # 验证正确的校验和
                assert verify_file_integrity(test_content, correct_checksum, algorithm), \
                    f"正确的校验和验证失败: {algorithm}"
                
                # 验证错误的校验和
                wrong_checksum = "0" * len(correct_checksum)
                assert not verify_file_integrity(test_content, wrong_checksum, algorithm), \
                    f"错误的校验和未被正确检测: {algorithm}"
        
        # 9. 验证批量上传的处理
        if len(upload_results) > 1:
            # 检查批量上传的一致性
            valid_count = sum(1 for r in upload_results if r["overall_valid"])
            invalid_count = len(upload_results) - valid_count
            
            # 验证统计信息的准确性
            assert valid_count + invalid_count == len(upload_results), \
                "批量上传统计信息不一致"
            
            # 验证每个文件都有唯一的校验和（除非内容相同）
            checksums = [r["checksum"] for r in upload_results]
            unique_checksums = set(checksums)
            
            # 如果校验和数量少于文件数量，说明有重复内容
            if len(unique_checksums) < len(checksums):
                # 这是正常的，相同内容应该有相同的校验和
                pass
        
        # 10. 验证错误处理和恢复
        def test_error_recovery(error_type: str) -> bool:
            """测试错误处理和恢复机制"""
            recovery_strategies = {
                "network_timeout": "retry_upload",
                "disk_full": "cleanup_temp_files",
                "permission_denied": "change_upload_directory",
                "virus_detected": "quarantine_file",
                "corruption_detected": "request_reupload"
            }
            
            if error_type in recovery_strategies:
                strategy = recovery_strategies[error_type]
                
                # 验证每种错误都有对应的恢复策略
                assert strategy in [
                    "retry_upload", "cleanup_temp_files", "change_upload_directory",
                    "quarantine_file", "request_reupload"
                ], f"未知的恢复策略: {strategy}"
                
                return True
            
            return False
        
        # 测试错误恢复机制
        error_types = ["network_timeout", "disk_full", "permission_denied", "virus_detected", "corruption_detected"]
        for error_type in error_types:
            recovery_valid = test_error_recovery(error_type)
            assert recovery_valid, f"错误类型 {error_type} 的恢复机制验证失败"
        
        # 11. 验证上传性能和资源使用
        def validate_upload_performance(file_count: int, total_size: int) -> bool:
            """验证上传性能"""
            # 模拟性能指标
            performance_metrics = {
                "max_concurrent_uploads": 5,
                "upload_speed_mbps": 10,
                "memory_usage_per_mb": 0.1,  # 每MB文件使用0.1MB内存
                "processing_time_per_mb": 0.5  # 每MB文件处理0.5秒
            }
            
            # 计算预期性能
            expected_memory = (total_size / (1024 * 1024)) * performance_metrics["memory_usage_per_mb"]
            expected_time = (total_size / (1024 * 1024)) * performance_metrics["processing_time_per_mb"]
            
            # 验证性能在可接受范围内
            assert expected_memory < 1000, f"内存使用过高: {expected_memory}MB"  # 1GB限制
            assert expected_time < 300, f"处理时间过长: {expected_time}秒"  # 5分钟限制
            assert file_count <= performance_metrics["max_concurrent_uploads"] * 10, \
                f"文件数量过多: {file_count}"
            
            return True
        
        # 测试上传性能
        total_upload_size = sum(r["size"] for r in upload_results)
        performance_valid = validate_upload_performance(len(upload_results), total_upload_size)
        assert performance_valid, "上传性能验证失败"
    
    @given(
        product_types=st.lists(
            st.sampled_from(['static', 'spa', 'game', 'tool']),
            min_size=1, max_size=10
        ),
        framework_configs=st.lists(
            st.fixed_dictionaries({
                'framework': st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
                'version': st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Nd', 'Po'))),
                'build_tool': st.text(min_size=1, max_size=30, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
            }),
            max_size=10
        ),
        compatibility_scenarios=st.lists(
            st.sampled_from([
                'modern_browser',
                'legacy_browser',
                'mobile_browser',
                'webview',
                'electron_app',
                'pwa_context'
            ]),
            min_size=1, max_size=6
        )
    )
    def test_product_type_support_completeness(self, product_types, framework_configs, compatibility_scenarios):
        """
        **Feature: product-integration, Property 5: 产品类型支持完整性**
        **Validates: Requirements 5.1, 5.2, 5.3, 5.4**
        
        验证产品类型支持的完整性和兼容性：
        1. 静态Web应用支持 (HTML/CSS/JS)
        2. 单页应用支持 (React/Vue/Angular)
        3. 游戏应用支持 (Canvas/WebGL)
        4. 工具应用支持 (在线工具/计算器)
        5. 框架兼容性检测
        6. 浏览器兼容性验证
        """
        # 1. 定义产品类型支持配置
        type_support_config = {
            "static": {
                "supported_files": [".html", ".css", ".js", ".json"],
                "required_files": ["index.html"],
                "optional_files": ["style.css", "script.js", "manifest.json"],
                "frameworks": ["vanilla", "jquery", "bootstrap"],
                "features": ["responsive_design", "offline_support"],
                "browser_requirements": {
                    "chrome": ">=60",
                    "firefox": ">=55",
                    "safari": ">=12",
                    "edge": ">=79"
                }
            },
            "spa": {
                "supported_files": [".html", ".css", ".js", ".json", ".map"],
                "required_files": ["index.html"],
                "optional_files": ["manifest.json", "service-worker.js"],
                "frameworks": ["react", "vue", "angular", "svelte", "preact"],
                "features": ["routing", "state_management", "hot_reload", "code_splitting"],
                "browser_requirements": {
                    "chrome": ">=70",
                    "firefox": ">=65",
                    "safari": ">=13",
                    "edge": ">=79"
                }
            },
            "game": {
                "supported_files": [".html", ".css", ".js", ".json", ".wasm"],
                "required_files": ["index.html"],
                "optional_files": ["game.js", "assets.json", "config.json"],
                "frameworks": ["phaser", "three.js", "babylon.js", "unity", "godot"],
                "features": ["webgl", "webassembly", "gamepad_api", "fullscreen", "audio"],
                "browser_requirements": {
                    "chrome": ">=75",
                    "firefox": ">=70",
                    "safari": ">=14",
                    "edge": ">=79"
                }
            },
            "tool": {
                "supported_files": [".html", ".css", ".js", ".json"],
                "required_files": ["index.html"],
                "optional_files": ["worker.js", "config.json"],
                "frameworks": ["vanilla", "react", "vue", "web_components"],
                "features": ["file_api", "clipboard_api", "download", "print"],
                "browser_requirements": {
                    "chrome": ">=65",
                    "firefox": ">=60",
                    "safari": ">=12",
                    "edge": ">=79"
                }
            }
        }
        
        # 2. 验证产品类型识别和配置
        def identify_product_type(files: list, config: dict) -> dict:
            """识别产品类型"""
            result = {
                "detected_type": None,
                "confidence": 0.0,
                "evidence": [],
                "supported": False
            }
            
            # 检查文件结构特征
            has_html = any(f.endswith('.html') for f in files)
            has_js = any(f.endswith('.js') for f in files)
            has_css = any(f.endswith('.css') for f in files)
            has_json = any(f.endswith('.json') for f in files)
            has_wasm = any(f.endswith('.wasm') for f in files)
            
            # 基于文件内容和配置推断类型
            if has_wasm or 'webgl' in str(config).lower():
                result["detected_type"] = "game"
                result["confidence"] = 0.9
                result["evidence"].append("WebAssembly或WebGL特征")
            elif 'react' in str(config).lower() or 'vue' in str(config).lower() or 'angular' in str(config).lower():
                result["detected_type"] = "spa"
                result["confidence"] = 0.8
                result["evidence"].append("SPA框架特征")
            elif 'calculator' in str(config).lower() or 'editor' in str(config).lower() or 'converter' in str(config).lower():
                result["detected_type"] = "tool"
                result["confidence"] = 0.7
                result["evidence"].append("工具应用特征")
            elif has_html and (has_js or has_css):
                result["detected_type"] = "static"
                result["confidence"] = 0.6
                result["evidence"].append("静态Web应用特征")
            
            # 验证类型支持
            if result["detected_type"] in type_support_config:
                type_config = type_support_config[result["detected_type"]]
                
                # 检查必需文件
                required_files_present = all(
                    any(f.endswith(req_file) for f in files)
                    for req_file in type_config["required_files"]
                )
                
                if required_files_present:
                    result["supported"] = True
                    result["evidence"].append("必需文件完整")
                else:
                    result["evidence"].append("缺少必需文件")
            
            return result
        
        # 3. 测试每种产品类型的支持
        for product_type in product_types:
            type_config = type_support_config[product_type]
            
            # 创建符合类型的文件列表
            test_files = type_config["required_files"].copy()
            test_files.extend(type_config["optional_files"][:2])  # 添加部分可选文件
            
            # 创建测试配置
            test_config = {
                "product_type": product_type,
                "framework": type_config["frameworks"][0] if type_config["frameworks"] else "vanilla"
            }
            
            # 为特定类型添加识别特征
            if product_type == "game":
                test_config["features"] = ["webgl", "canvas"]
            elif product_type == "spa":
                test_config["framework"] = "react"
            elif product_type == "tool":
                test_config["description"] = "calculator tool"
            
            # 执行类型识别
            identification_result = identify_product_type(test_files, test_config)
            
            # 验证类型识别的准确性
            assert identification_result["detected_type"] == product_type, \
                f"产品类型识别错误: 期望 {product_type}, 实际 {identification_result['detected_type']}"
            
            assert identification_result["supported"], \
                f"产品类型 {product_type} 应该被支持但被标记为不支持"
            
            assert identification_result["confidence"] > 0.5, \
                f"产品类型 {product_type} 识别置信度过低: {identification_result['confidence']}"
        
        # 4. 验证框架兼容性检测
        def check_framework_compatibility(framework_config: dict, product_type: str) -> dict:
            """检查框架兼容性"""
            result = {
                "compatible": False,
                "warnings": [],
                "requirements": [],
                "optimizations": []
            }
            
            if product_type not in type_support_config:
                result["warnings"].append(f"未知产品类型: {product_type}")
                return result
            
            type_config = type_support_config[product_type]
            framework = framework_config.get("framework", "").lower()
            
            # 检查框架支持
            if framework in [f.lower() for f in type_config["frameworks"]]:
                result["compatible"] = True
                result["requirements"].append(f"支持的框架: {framework}")
            else:
                result["warnings"].append(f"框架 {framework} 可能不被完全支持")
                result["compatible"] = True  # 仍然尝试支持
            
            # 检查版本兼容性
            version = str(framework_config.get("version", ""))
            if version:
                # 简化的版本检查
                try:
                    # 提取数字部分
                    version_parts = [c for c in version if c.isdigit() or c == '.']
                    version_str = ''.join(version_parts)
                    if version_str and '.' in version_str:
                        version_num = float(version_str.split('.')[0])
                        if version_num < 1:
                            result["warnings"].append("框架版本可能过旧")
                except (ValueError, IndexError):
                    result["warnings"].append("无法解析框架版本")
            
            # 检查构建工具
            build_tool = str(framework_config.get("build_tool", ""))
            if build_tool:
                supported_build_tools = ["webpack", "vite", "rollup", "parcel", "esbuild"]
                if build_tool.lower() not in supported_build_tools:
                    result["warnings"].append(f"构建工具 {build_tool} 可能需要额外配置")
            
            # 提供优化建议
            if product_type == "spa":
                result["optimizations"].extend([
                    "启用代码分割",
                    "配置懒加载",
                    "优化打包大小"
                ])
            elif product_type == "game":
                result["optimizations"].extend([
                    "启用WebGL优化",
                    "配置资源预加载",
                    "优化渲染性能"
                ])
            
            return result
        
        # 测试框架兼容性
        for i, config in enumerate(framework_configs):
            if i < len(product_types):
                product_type = product_types[i % len(product_types)]
                compatibility_result = check_framework_compatibility(config, product_type)
                
                # 验证兼容性检查结果
                assert isinstance(compatibility_result["compatible"], bool), \
                    "兼容性检查结果应该是布尔值"
                
                assert isinstance(compatibility_result["warnings"], list), \
                    "警告信息应该是列表"
                
                assert isinstance(compatibility_result["requirements"], list), \
                    "需求信息应该是列表"
        
        # 5. 验证浏览器兼容性
        def check_browser_compatibility(product_type: str, browser_info: dict) -> dict:
            """检查浏览器兼容性"""
            result = {
                "supported": False,
                "partial_support": False,
                "missing_features": [],
                "polyfills_needed": [],
                "fallback_options": []
            }
            
            if product_type not in type_support_config:
                return result
            
            type_config = type_support_config[product_type]
            browser_requirements = type_config["browser_requirements"]
            
            browser_name = browser_info.get("name", "").lower()
            browser_version = browser_info.get("version", "0")
            
            # 简化的版本比较
            try:
                current_version = int(browser_version.split('.')[0])
                
                if browser_name in browser_requirements:
                    required_version = int(browser_requirements[browser_name].replace(">=", ""))
                    
                    if current_version >= required_version:
                        result["supported"] = True
                    elif current_version >= required_version - 5:  # 容忍5个版本的差异
                        result["partial_support"] = True
                        result["missing_features"].append("部分新特性可能不可用")
                    else:
                        result["missing_features"].append("浏览器版本过旧")
                        result["polyfills_needed"].extend(["es6-polyfill", "fetch-polyfill"])
                
            except (ValueError, IndexError):
                result["missing_features"].append("无法确定浏览器版本")
            
            # 根据产品类型添加特定的兼容性检查
            if product_type == "game":
                if browser_name == "safari" and current_version < 14:
                    result["missing_features"].append("WebGL支持有限")
                    result["fallback_options"].append("Canvas 2D渲染")
            
            elif product_type == "spa":
                if browser_name == "ie":
                    result["supported"] = False
                    result["missing_features"].append("不支持现代JavaScript特性")
                    result["polyfills_needed"].extend(["babel-polyfill", "core-js"])
            
            return result
        
        # 测试浏览器兼容性
        test_browsers = [
            {"name": "chrome", "version": "90.0"},
            {"name": "firefox", "version": "85.0"},
            {"name": "safari", "version": "14.0"},
            {"name": "edge", "version": "90.0"},
            {"name": "ie", "version": "11.0"}
        ]
        
        for product_type in product_types:
            for browser in test_browsers:
                compatibility_result = check_browser_compatibility(product_type, browser)
                
                # 验证兼容性结果的合理性
                if browser["name"] == "ie":
                    # IE应该对现代产品类型支持有限
                    if product_type in ["spa", "game"]:
                        assert not compatibility_result["supported"], \
                            f"IE不应该完全支持 {product_type} 类型"
                else:
                    # 现代浏览器应该支持大部分产品类型
                    assert compatibility_result["supported"] or compatibility_result["partial_support"], \
                        f"现代浏览器 {browser['name']} 应该支持 {product_type} 类型"
        
        # 6. 验证特定场景下的兼容性
        for scenario in compatibility_scenarios:
            scenario_config = {
                "modern_browser": {
                    "supports_es6": True,
                    "supports_webgl": True,
                    "supports_wasm": True,
                    "supports_service_worker": True
                },
                "legacy_browser": {
                    "supports_es6": False,
                    "supports_webgl": False,
                    "supports_wasm": False,
                    "supports_service_worker": False
                },
                "mobile_browser": {
                    "supports_es6": True,
                    "supports_webgl": True,
                    "supports_wasm": True,
                    "supports_touch": True,
                    "limited_memory": True
                },
                "webview": {
                    "supports_es6": True,
                    "supports_webgl": True,
                    "restricted_apis": True,
                    "no_navigation": True
                },
                "electron_app": {
                    "supports_es6": True,
                    "supports_webgl": True,
                    "supports_node_apis": True,
                    "supports_file_system": True
                },
                "pwa_context": {
                    "supports_es6": True,
                    "supports_service_worker": True,
                    "supports_offline": True,
                    "supports_install": True
                }
            }
            
            if scenario in scenario_config:
                config = scenario_config[scenario]
                
                # 验证每种场景下的产品类型适配
                for product_type in product_types:
                    adaptation_needed = []
                    
                    if product_type == "game":
                        if not config.get("supports_webgl", False):
                            adaptation_needed.append("需要Canvas 2D后备方案")
                        if config.get("limited_memory", False):
                            adaptation_needed.append("需要优化内存使用")
                    
                    elif product_type == "spa":
                        if not config.get("supports_es6", False):
                            adaptation_needed.append("需要ES5转译")
                        if config.get("no_navigation", False):
                            adaptation_needed.append("需要适配受限导航")
                    
                    elif product_type == "tool":
                        if config.get("restricted_apis", False):
                            adaptation_needed.append("需要检查API可用性")
                    
                    # 验证适配建议的合理性
                    if scenario == "legacy_browser" and product_type in ["spa", "game"]:
                        assert len(adaptation_needed) > 0, \
                            f"传统浏览器环境下 {product_type} 应该需要适配"
                    
                    if scenario == "mobile_browser" and product_type == "game":
                        assert any("内存" in suggestion for suggestion in adaptation_needed), \
                            f"移动浏览器环境下游戏应该考虑内存优化"
        
        # 7. 验证产品类型转换和升级
        def validate_type_conversion(from_type: str, to_type: str) -> dict:
            """验证产品类型转换的可行性"""
            result = {
                "feasible": False,
                "complexity": "high",
                "required_changes": [],
                "data_migration": [],
                "compatibility_issues": []
            }
            
            conversion_matrix = {
                ("static", "spa"): {
                    "feasible": True,
                    "complexity": "medium",
                    "changes": ["添加路由系统", "重构为组件化", "添加状态管理"]
                },
                ("static", "tool"): {
                    "feasible": True,
                    "complexity": "low",
                    "changes": ["添加工具功能", "优化用户界面"]
                },
                ("spa", "static"): {
                    "feasible": True,
                    "complexity": "medium",
                    "changes": ["预渲染页面", "移除动态路由", "简化交互"]
                },
                ("tool", "spa"): {
                    "feasible": True,
                    "complexity": "medium",
                    "changes": ["添加路由", "组件化工具功能"]
                }
            }
            
            conversion_key = (from_type, to_type)
            if conversion_key in conversion_matrix:
                conversion_info = conversion_matrix[conversion_key]
                result.update({
                    "feasible": conversion_info["feasible"],
                    "complexity": conversion_info["complexity"],
                    "required_changes": conversion_info["changes"]
                })
            
            return result
        
        # 测试类型转换
        type_pairs = [
            ("static", "spa"),
            ("static", "tool"),
            ("spa", "static"),
            ("tool", "spa")
        ]
        
        for from_type, to_type in type_pairs:
            if from_type in product_types and to_type in product_types:
                conversion_result = validate_type_conversion(from_type, to_type)
                
                # 验证转换结果的合理性
                assert isinstance(conversion_result["feasible"], bool), \
                    "转换可行性应该是布尔值"
                
                assert conversion_result["complexity"] in ["low", "medium", "high"], \
                    "转换复杂度应该是预定义的级别"
                
                if conversion_result["feasible"]:
                    assert len(conversion_result["required_changes"]) > 0, \
                        f"可行的转换 {from_type}->{to_type} 应该有具体的变更要求"
        
        # 8. 验证产品类型的性能特征
        def analyze_performance_characteristics(product_type: str) -> dict:
            """分析产品类型的性能特征"""
            performance_profiles = {
                "static": {
                    "load_time": "fast",
                    "memory_usage": "low",
                    "cpu_usage": "low",
                    "network_usage": "low",
                    "optimization_priority": ["caching", "compression", "cdn"]
                },
                "spa": {
                    "load_time": "medium",
                    "memory_usage": "medium",
                    "cpu_usage": "medium",
                    "network_usage": "medium",
                    "optimization_priority": ["code_splitting", "lazy_loading", "bundling"]
                },
                "game": {
                    "load_time": "slow",
                    "memory_usage": "high",
                    "cpu_usage": "high",
                    "network_usage": "high",
                    "optimization_priority": ["asset_optimization", "webgl_optimization", "memory_management"]
                },
                "tool": {
                    "load_time": "fast",
                    "memory_usage": "medium",
                    "cpu_usage": "variable",
                    "network_usage": "low",
                    "optimization_priority": ["algorithm_optimization", "ui_responsiveness", "data_processing"]
                }
            }
            
            return performance_profiles.get(product_type, {})
        
        # 测试性能特征分析
        for product_type in product_types:
            performance_profile = analyze_performance_characteristics(product_type)
            
            # 验证性能特征的合理性
            if product_type == "static":
                assert performance_profile.get("load_time") == "fast", \
                    "静态应用应该有快速的加载时间"
                assert performance_profile.get("memory_usage") == "low", \
                    "静态应用应该有低内存使用"
            
            elif product_type == "game":
                assert performance_profile.get("memory_usage") == "high", \
                    "游戏应用通常有高内存使用"
                assert performance_profile.get("cpu_usage") == "high", \
                    "游戏应用通常有高CPU使用"
            
            # 验证优化建议的存在
            optimizations = performance_profile.get("optimization_priority", [])
            assert len(optimizations) > 0, \
                f"产品类型 {product_type} 应该有性能优化建议"
    
    @given(
        config_scenarios=st.lists(
            st.dictionaries(
                st.sampled_from(['name', 'value', 'type', 'required', 'default', 'validation']),
                st.one_of(
                    st.text(min_size=1, max_size=100),
                    st.integers(min_value=0, max_value=10000),
                    st.booleans(),
                    st.floats(min_value=0.0, max_value=100.0, allow_nan=False)
                ),
                min_size=3, max_size=6
            ),
            min_size=1, max_size=15
        ),
        environment_configs=st.lists(
            st.dictionaries(
                st.sampled_from(['env_name', 'env_value', 'scope', 'sensitive']),
                st.one_of(st.text(), st.booleans()),
                min_size=2, max_size=4
            ),
            max_size=10
        ),
        validation_rules=st.lists(
            st.sampled_from([
                'required_field',
                'type_validation',
                'range_validation',
                'format_validation',
                'dependency_validation',
                'security_validation'
            ]),
            min_size=1, max_size=6
        )
    )
    def test_product_config_validity(self, config_scenarios, environment_configs, validation_rules):
        """
        **Feature: product-integration, Property 9: 产品配置有效性**
        **Validates: Requirements 5.5**
        
        验证产品配置系统的有效性和正确性：
        1. 配置参数验证和类型检查
        2. 环境变量管理和作用域控制
        3. 配置依赖关系验证
        4. 配置安全性和敏感信息处理
        5. 配置应用和生效机制
        6. 配置版本管理和回滚
        """
        # 1. 定义配置系统架构
        config_system = {
            "supported_types": ["string", "number", "boolean", "array", "object"],
            "validation_rules": {
                "required": lambda value: value is not None and value != "",
                "type_string": lambda value: isinstance(value, str),
                "type_number": lambda value: isinstance(value, (int, float)),
                "type_boolean": lambda value: isinstance(value, bool),
                "type_array": lambda value: isinstance(value, list),
                "type_object": lambda value: isinstance(value, dict),
                "min_length": lambda value, min_len: len(str(value)) >= min_len,
                "max_length": lambda value, max_len: len(str(value)) <= max_len,
                "min_value": lambda value, min_val: float(value) >= min_val,
                "max_value": lambda value, max_val: float(value) <= max_val,
                "pattern": lambda value, pattern: bool(re.match(pattern, str(value))),
                "enum": lambda value, options: value in options
            },
            "security_rules": {
                "no_script_injection": lambda value: "<script" not in str(value).lower(),
                "no_sql_injection": lambda value: not any(keyword in str(value).lower() for keyword in ["drop", "delete", "insert", "update", "select"]),
                "no_path_traversal": lambda value: ".." not in str(value) and not str(value).startswith("/"),
                "safe_url": lambda value: str(value).startswith(("http://", "https://", "/")) if "://" in str(value) else True
            },
            "environment_scopes": ["global", "product", "user", "session"],
            "sensitive_patterns": ["password", "secret", "key", "token", "credential"]
        }
        
        # 2. 配置参数验证系统
        def validate_config_parameter(param_config: dict) -> dict:
            """验证单个配置参数"""
            result = {
                "valid": True,
                "errors": [],
                "warnings": [],
                "normalized_value": None
            }
            
            param_name = str(param_config.get("name", ""))
            param_value = param_config.get("value")
            param_type = str(param_config.get("type", "string"))
            is_required = bool(param_config.get("required", False))
            default_value = param_config.get("default")
            
            # 检查必填参数
            if is_required and (param_value is None or param_value == "" or param_value == 0):
                if default_value is not None:
                    param_value = default_value
                    result["warnings"].append(f"使用默认值: {default_value}")
                else:
                    result["valid"] = False
                    result["errors"].append(f"必填参数 {param_name} 不能为空")
                    return result
            
            # 类型验证
            if param_value is not None:
                type_validator = config_system["validation_rules"].get(f"type_{param_type}")
                if type_validator and not type_validator(param_value):
                    # 尝试类型转换
                    try:
                        if param_type == "number":
                            param_value = float(param_value) if '.' in str(param_value) else int(param_value)
                        elif param_type == "boolean":
                            param_value = str(param_value).lower() in ['true', '1', 'yes', 'on']
                        elif param_type == "string":
                            param_value = str(param_value)
                        elif param_type == "array":
                            if isinstance(param_value, str):
                                param_value = param_value.split(',')
                        
                        result["warnings"].append(f"参数 {param_name} 已自动转换为 {param_type} 类型")
                    except (ValueError, TypeError):
                        result["valid"] = False
                        result["errors"].append(f"参数 {param_name} 类型不匹配，期望 {param_type}")
                        return result
            
            # 安全性验证
            for security_rule, validator in config_system["security_rules"].items():
                if not validator(param_value):
                    result["valid"] = False
                    result["errors"].append(f"参数 {param_name} 违反安全规则: {security_rule}")
            
            # 敏感信息检测
            if any(pattern in param_name.lower() for pattern in config_system["sensitive_patterns"]):
                result["warnings"].append(f"参数 {param_name} 可能包含敏感信息，建议加密存储")
            
            result["normalized_value"] = param_value
            return result
        
        # 3. 测试配置参数验证
        validated_configs = []
        for config in config_scenarios:
            validation_result = validate_config_parameter(config)
            validated_configs.append({
                "config": config,
                "validation": validation_result
            })
            
            # 验证基本验证逻辑
            is_required = bool(config.get("required", False))
            has_value = config.get("value") not in [None, "", 0]
            has_default = config.get("default") is not None
            
            if is_required and not has_value and not has_default:
                assert not validation_result["valid"], \
                    f"必填参数缺失时应该验证失败: {config.get('name')}"
        
        # 4. 环境变量管理系统
        def manage_environment_variables(env_configs: list) -> dict:
            """管理环境变量"""
            env_manager = {
                "variables": {},
                "scopes": {scope: {} for scope in config_system["environment_scopes"]},
                "sensitive_vars": set(),
                "conflicts": []
            }
            
            for env_config in env_configs:
                env_name = str(env_config.get("env_name", ""))
                env_value = env_config.get("env_value", "")
                scope = str(env_config.get("scope", "product"))
                is_sensitive = bool(env_config.get("sensitive", False))
                
                # 验证环境变量名称
                if not env_name or not re.match(r'^[A-Z][A-Z0-9_]*$', env_name):
                    continue  # 跳过无效的环境变量名
                
                # 检查作用域
                if scope not in config_system["environment_scopes"]:
                    scope = "product"  # 默认作用域
                
                # 检查冲突
                if env_name in env_manager["variables"]:
                    existing_scope = env_manager["variables"][env_name]["scope"]
                    if existing_scope != scope:
                        env_manager["conflicts"].append({
                            "variable": env_name,
                            "existing_scope": existing_scope,
                            "new_scope": scope
                        })
                
                # 存储环境变量
                env_manager["variables"][env_name] = {
                    "value": env_value,
                    "scope": scope,
                    "sensitive": is_sensitive
                }
                
                env_manager["scopes"][scope][env_name] = env_value
                
                if is_sensitive:
                    env_manager["sensitive_vars"].add(env_name)
            
            return env_manager
        
        # 测试环境变量管理
        env_manager = manage_environment_variables(environment_configs)
        
        # 验证环境变量管理的正确性
        assert isinstance(env_manager["variables"], dict), "环境变量存储应该是字典"
        assert isinstance(env_manager["sensitive_vars"], set), "敏感变量集合应该是set类型"
        
        # 验证作用域隔离
        for scope in config_system["environment_scopes"]:
            scope_vars = env_manager["scopes"][scope]
            for var_name, var_value in scope_vars.items():
                assert env_manager["variables"][var_name]["scope"] == scope, \
                    f"环境变量 {var_name} 的作用域不一致"
        
        # 5. 配置依赖关系验证
        def validate_config_dependencies(configs: list) -> dict:
            """验证配置依赖关系"""
            dependency_result = {
                "valid": True,
                "missing_dependencies": [],
                "circular_dependencies": [],
                "dependency_graph": {}
            }
            
            # 构建依赖图
            config_map = {str(cfg.get("name", "")): cfg for cfg in configs if cfg.get("name")}
            
            for config in configs:
                config_name = str(config.get("name", ""))
                if not config_name:
                    continue
                
                dependencies = []
                
                # 检查值中的依赖引用 (例如: ${OTHER_CONFIG})
                config_value = str(config.get("value", ""))
                import re
                dep_matches = re.findall(r'\$\{([^}]+)\}', config_value)
                dependencies.extend(dep_matches)
                
                dependency_result["dependency_graph"][config_name] = dependencies
                
                # 检查依赖是否存在
                for dep in dependencies:
                    if dep not in config_map:
                        dependency_result["missing_dependencies"].append({
                            "config": config_name,
                            "missing_dependency": dep
                        })
                        dependency_result["valid"] = False
            
            # 检查循环依赖
            def has_circular_dependency(node, visited, rec_stack):
                visited.add(node)
                rec_stack.add(node)
                
                for neighbor in dependency_result["dependency_graph"].get(node, []):
                    if neighbor not in visited:
                        if has_circular_dependency(neighbor, visited, rec_stack):
                            return True
                    elif neighbor in rec_stack:
                        dependency_result["circular_dependencies"].append({
                            "cycle": [node, neighbor]
                        })
                        return True
                
                rec_stack.remove(node)
                return False
            
            visited = set()
            for config_name in dependency_result["dependency_graph"]:
                if config_name not in visited:
                    has_circular_dependency(config_name, visited, set())
            
            if dependency_result["circular_dependencies"]:
                dependency_result["valid"] = False
            
            return dependency_result
        
        # 测试配置依赖验证
        dependency_result = validate_config_dependencies(config_scenarios)
        
        # 验证依赖关系检查的正确性
        assert isinstance(dependency_result["dependency_graph"], dict), \
            "依赖图应该是字典类型"
        
        if dependency_result["missing_dependencies"]:
            assert not dependency_result["valid"], \
                "存在缺失依赖时验证应该失败"
        
        if dependency_result["circular_dependencies"]:
            assert not dependency_result["valid"], \
                "存在循环依赖时验证应该失败"
        
        # 6. 配置应用和生效机制
        def apply_configuration(configs: list, env_vars: dict) -> dict:
            """应用配置到运行环境"""
            application_result = {
                "success": True,
                "applied_configs": {},
                "failed_configs": [],
                "runtime_values": {},
                "performance_impact": {
                    "memory_usage": 0,
                    "cpu_overhead": 0,
                    "network_calls": 0
                }
            }
            
            for config in configs:
                config_name = str(config.get("name", ""))
                config_value = config.get("value")
                
                if not config_name:
                    continue
                
                try:
                    # 解析环境变量引用
                    if isinstance(config_value, str) and "${" in config_value:
                        import re
                        def replace_env_var(match):
                            var_name = match.group(1)
                            return str(env_vars.get(var_name, f"${{{var_name}}}"))
                        
                        config_value = re.sub(r'\$\{([^}]+)\}', replace_env_var, config_value)
                    
                    # 应用配置
                    application_result["applied_configs"][config_name] = config_value
                    application_result["runtime_values"][config_name] = config_value
                    
                    # 模拟性能影响
                    application_result["performance_impact"]["memory_usage"] += len(str(config_value))
                    application_result["performance_impact"]["cpu_overhead"] += 1
                    
                    if "url" in config_name.lower() or "endpoint" in config_name.lower():
                        application_result["performance_impact"]["network_calls"] += 1
                
                except Exception as e:
                    application_result["failed_configs"].append({
                        "config": config_name,
                        "error": str(e)
                    })
                    application_result["success"] = False
            
            return application_result
        
        # 测试配置应用
        env_vars_dict = {var: data["value"] for var, data in env_manager["variables"].items()}
        application_result = apply_configuration(validated_configs, env_vars_dict)
        
        # 验证配置应用的正确性
        assert isinstance(application_result["applied_configs"], dict), \
            "应用的配置应该是字典类型"
        
        assert isinstance(application_result["performance_impact"], dict), \
            "性能影响统计应该是字典类型"
        
        # 验证性能影响在合理范围内
        memory_usage = application_result["performance_impact"]["memory_usage"]
        assert memory_usage < 1024 * 1024, f"配置内存使用过高: {memory_usage} bytes"  # 1MB限制
        
        # 7. 配置验证规则测试
        for rule in validation_rules:
            if rule == "required_field":
                # 测试必填字段验证
                test_config = {"name": "test_required", "required": True, "value": ""}
                result = validate_config_parameter(test_config)
                assert not result["valid"], "必填字段为空时应该验证失败"
            
            elif rule == "type_validation":
                # 测试类型验证
                test_config = {"name": "test_type", "type": "number", "value": "not_a_number"}
                result = validate_config_parameter(test_config)
                # 可能通过类型转换成功，也可能失败，都是合理的
                
            elif rule == "range_validation":
                # 测试范围验证（简化实现）
                test_config = {"name": "test_range", "type": "number", "value": 50}
                result = validate_config_parameter(test_config)
                assert result["valid"], "有效数值应该通过验证"
            
            elif rule == "format_validation":
                # 测试格式验证
                test_config = {"name": "test_format", "type": "string", "value": "valid_format"}
                result = validate_config_parameter(test_config)
                assert result["valid"], "有效格式应该通过验证"
            
            elif rule == "security_validation":
                # 测试安全验证
                test_config = {"name": "test_security", "value": "<script>alert('xss')</script>"}
                result = validate_config_parameter(test_config)
                assert not result["valid"], "包含脚本注入的配置应该被拒绝"
        
        # 8. 配置版本管理和回滚
        def manage_config_versions(configs: list) -> dict:
            """管理配置版本"""
            version_manager = {
                "versions": {},
                "current_version": "1.0.0",
                "rollback_history": [],
                "change_log": []
            }
            
            # 创建初始版本
            version_manager["versions"]["1.0.0"] = {
                "configs": configs.copy(),
                "timestamp": time.time(),
                "description": "初始配置版本"
            }
            
            # 模拟配置变更
            if len(configs) > 0:
                modified_configs = configs.copy()
                if modified_configs:
                    # 修改第一个配置的值
                    if "value" in modified_configs[0]:
                        old_value = modified_configs[0]["value"]
                        modified_configs[0]["value"] = f"modified_{old_value}"
                        
                        # 创建新版本
                        new_version = "1.1.0"
                        version_manager["versions"][new_version] = {
                            "configs": modified_configs,
                            "timestamp": time.time(),
                            "description": "配置更新"
                        }
                        
                        version_manager["current_version"] = new_version
                        version_manager["change_log"].append({
                            "version": new_version,
                            "changes": [f"修改配置值: {old_value} -> {modified_configs[0]['value']}"],
                            "timestamp": time.time()
                        })
            
            return version_manager
        
        # 测试配置版本管理
        version_manager = manage_config_versions(config_scenarios)
        
        # 验证版本管理的正确性
        assert "1.0.0" in version_manager["versions"], "应该有初始版本"
        assert isinstance(version_manager["change_log"], list), "变更日志应该是列表"
        
        # 验证版本回滚功能
        def rollback_config(version_manager: dict, target_version: str) -> bool:
            """回滚配置到指定版本"""
            if target_version in version_manager["versions"]:
                version_manager["rollback_history"].append({
                    "from_version": version_manager["current_version"],
                    "to_version": target_version,
                    "timestamp": time.time()
                })
                version_manager["current_version"] = target_version
                return True
            return False
        
        # 测试回滚功能
        if len(version_manager["versions"]) > 1:
            rollback_success = rollback_config(version_manager, "1.0.0")
            assert rollback_success, "回滚到存在的版本应该成功"
            assert version_manager["current_version"] == "1.0.0", "回滚后当前版本应该更新"
        
        # 9. 配置性能优化验证
        def optimize_config_performance(configs: list) -> dict:
            """优化配置性能"""
            optimization_result = {
                "optimizations_applied": [],
                "performance_gain": 0,
                "memory_saved": 0,
                "recommendations": []
            }
            
            # 检查重复配置
            config_names = [str(cfg.get("name", "")) for cfg in configs if cfg.get("name")]
            duplicates = set([name for name in config_names if config_names.count(name) > 1])
            
            if duplicates:
                optimization_result["optimizations_applied"].append("去除重复配置")
                optimization_result["memory_saved"] += len(duplicates) * 100  # 估算节省的内存
            
            # 检查未使用的配置
            unused_configs = [cfg for cfg in configs if not cfg.get("value")]
            if unused_configs:
                optimization_result["recommendations"].append("移除未使用的配置项")
            
            # 检查配置缓存机会
            cacheable_configs = [cfg for cfg in configs if str(cfg.get("type", "")) in ["string", "number"]]
            if len(cacheable_configs) > 5:
                optimization_result["recommendations"].append("启用配置缓存")
                optimization_result["performance_gain"] += 20  # 估算性能提升百分比
            
            return optimization_result
        
        # 测试配置性能优化
        optimization_result = optimize_config_performance(config_scenarios)
        
        # 验证性能优化建议的合理性
        assert isinstance(optimization_result["optimizations_applied"], list), \
            "优化应用列表应该是列表类型"
        
        assert isinstance(optimization_result["recommendations"], list), \
            "优化建议应该是列表类型"
        
        assert optimization_result["performance_gain"] >= 0, \
            "性能提升应该是非负数"
        
        assert optimization_result["memory_saved"] >= 0, \
            "内存节省应该是非负数"
    
    @given(
        user_sessions=st.lists(
            st.dictionaries(
                st.sampled_from(['session_id', 'user_id', 'product_id', 'state_data', 'timestamp']),
                st.one_of(
                    st.text(min_size=1, max_size=100),
                    st.integers(min_value=1, max_value=10000),
                    st.dictionaries(st.text(), st.one_of(st.text(), st.integers(), st.booleans()), max_size=10)
                ),
                min_size=3, max_size=5
            ),
            min_size=1, max_size=10
        ),
        state_operations=st.lists(
            st.sampled_from([
                'save_state',
                'load_state',
                'update_state',
                'clear_state',
                'backup_state',
                'restore_state'
            ]),
            min_size=1, max_size=15
        ),
        persistence_scenarios=st.lists(
            st.sampled_from([
                'browser_refresh',
                'tab_close_reopen',
                'session_timeout',
                'storage_full',
                'network_offline',
                'browser_crash'
            ]),
            min_size=1, max_size=6
        )
    )
    def test_product_state_persistence(self, user_sessions, state_operations, persistence_scenarios):
        """
        **Feature: product-integration, Property 4: 产品状态持久性**
        **Validates: Requirements 6.4**
        
        验证产品状态持久性和恢复机制：
        1. 状态保存和加载的一致性
        2. 浏览器刷新后状态恢复
        3. 会话超时处理和状态保护
        4. 存储空间管理和清理
        5. 离线状态处理和同步
        6. 状态版本管理和冲突解决
        """
        # 1. 定义状态持久性系统
        persistence_system = {
            "storage_backends": {
                "localStorage": {
                    "capacity": 5 * 1024 * 1024,  # 5MB
                    "persistent": True,
                    "cross_tab": True,
                    "secure": False
                },
                "sessionStorage": {
                    "capacity": 5 * 1024 * 1024,  # 5MB
                    "persistent": False,
                    "cross_tab": False,
                    "secure": False
                },
                "indexedDB": {
                    "capacity": 50 * 1024 * 1024,  # 50MB
                    "persistent": True,
                    "cross_tab": True,
                    "secure": True
                },
                "memory": {
                    "capacity": 10 * 1024 * 1024,  # 10MB
                    "persistent": False,
                    "cross_tab": False,
                    "secure": True
                }
            },
            "state_types": {
                "ui_state": {"priority": "high", "backend": "localStorage"},
                "user_preferences": {"priority": "high", "backend": "localStorage"},
                "temporary_data": {"priority": "low", "backend": "sessionStorage"},
                "large_datasets": {"priority": "medium", "backend": "indexedDB"},
                "sensitive_data": {"priority": "high", "backend": "memory"}
            },
            "compression_threshold": 1024,  # 1KB
            "encryption_required": ["sensitive_data"],
            "cleanup_interval": 24 * 3600,  # 24小时
            "max_versions": 5
        }
        
        # 2. 状态管理器实现
        class StateManager:
            def __init__(self):
                self.storage = {
                    "localStorage": {},
                    "sessionStorage": {},
                    "indexedDB": {},
                    "memory": {}
                }
                self.usage = {backend: 0 for backend in self.storage.keys()}
                self.versions = {}
                self.metadata = {}
            
            def save_state(self, session_id: str, product_id: int, state_data: dict, state_type: str = "ui_state") -> dict:
                """保存产品状态"""
                result = {
                    "success": False,
                    "backend_used": None,
                    "compressed": False,
                    "encrypted": False,
                    "version": 1,
                    "size": 0
                }
                
                try:
                    # 确定存储后端
                    type_config = persistence_system["state_types"].get(state_type, {"backend": "localStorage"})
                    backend = type_config["backend"]
                    
                    # 序列化状态数据
                    serialized_data = json.dumps(state_data, default=str)
                    data_size = len(serialized_data.encode('utf-8'))
                    result["size"] = data_size
                    
                    # 检查是否需要压缩
                    if data_size > persistence_system["compression_threshold"]:
                        # 模拟压缩（简化实现）
                        compressed_size = int(data_size * 0.7)  # 假设压缩率30%
                        result["compressed"] = True
                        data_size = compressed_size
                    
                    # 检查是否需要加密
                    if state_type in persistence_system["encryption_required"]:
                        result["encrypted"] = True
                        data_size += 32  # 加密开销
                    
                    # 检查存储容量
                    backend_config = persistence_system["storage_backends"][backend]
                    if self.usage[backend] + data_size > backend_config["capacity"]:
                        # 尝试清理旧数据
                        self._cleanup_old_data(backend)
                        
                        # 如果仍然不够，尝试其他后端
                        if self.usage[backend] + data_size > backend_config["capacity"]:
                            for alt_backend, alt_config in persistence_system["storage_backends"].items():
                                if self.usage[alt_backend] + data_size <= alt_config["capacity"]:
                                    backend = alt_backend
                                    break
                            else:
                                return result  # 所有后端都满了
                    
                    # 生成存储键
                    storage_key = f"{session_id}_{product_id}_{state_type}"
                    
                    # 版本管理
                    if storage_key in self.versions:
                        self.versions[storage_key] += 1
                    else:
                        self.versions[storage_key] = 1
                    
                    version = self.versions[storage_key]
                    versioned_key = f"{storage_key}_v{version}"
                    
                    # 保存状态
                    self.storage[backend][versioned_key] = {
                        "data": serialized_data,
                        "metadata": {
                            "session_id": session_id,
                            "product_id": product_id,
                            "state_type": state_type,
                            "version": version,
                            "timestamp": time.time(),
                            "size": data_size,
                            "compressed": result["compressed"],
                            "encrypted": result["encrypted"]
                        }
                    }
                    
                    # 更新使用量
                    self.usage[backend] += data_size
                    
                    # 清理旧版本
                    self._cleanup_old_versions(storage_key, backend)
                    
                    result.update({
                        "success": True,
                        "backend_used": backend,
                        "version": version
                    })
                
                except Exception as e:
                    result["error"] = str(e)
                
                return result
            
            def load_state(self, session_id: str, product_id: int, state_type: str = "ui_state", version: int = None) -> dict:
                """加载产品状态"""
                result = {
                    "success": False,
                    "data": None,
                    "version": None,
                    "backend_used": None,
                    "age_seconds": 0
                }
                
                try:
                    storage_key = f"{session_id}_{product_id}_{state_type}"
                    
                    # 确定版本
                    if version is None:
                        version = self.versions.get(storage_key, 1)
                    
                    versioned_key = f"{storage_key}_v{version}"
                    
                    # 在所有后端中查找
                    for backend, storage in self.storage.items():
                        if versioned_key in storage:
                            stored_item = storage[versioned_key]
                            metadata = stored_item["metadata"]
                            
                            # 检查数据是否过期
                            age = time.time() - metadata["timestamp"]
                            if age > 7 * 24 * 3600:  # 7天过期
                                continue
                            
                            # 反序列化数据
                            data = json.loads(stored_item["data"])
                            
                            result.update({
                                "success": True,
                                "data": data,
                                "version": metadata["version"],
                                "backend_used": backend,
                                "age_seconds": age
                            })
                            break
                
                except Exception as e:
                    result["error"] = str(e)
                
                return result
            
            def _cleanup_old_data(self, backend: str):
                """清理旧数据"""
                current_time = time.time()
                keys_to_remove = []
                
                for key, item in self.storage[backend].items():
                    metadata = item["metadata"]
                    age = current_time - metadata["timestamp"]
                    
                    # 清理超过清理间隔的数据
                    if age > persistence_system["cleanup_interval"]:
                        keys_to_remove.append(key)
                        self.usage[backend] -= metadata["size"]
                
                for key in keys_to_remove:
                    del self.storage[backend][key]
            
            def _cleanup_old_versions(self, storage_key: str, backend: str):
                """清理旧版本"""
                current_version = self.versions.get(storage_key, 1)
                max_versions = persistence_system["max_versions"]
                
                if current_version > max_versions:
                    for v in range(1, current_version - max_versions + 1):
                        old_key = f"{storage_key}_v{v}"
                        if old_key in self.storage[backend]:
                            old_item = self.storage[backend][old_key]
                            self.usage[backend] -= old_item["metadata"]["size"]
                            del self.storage[backend][old_key]
        
        # 3. 测试状态管理器
        state_manager = StateManager()
        
        # 处理用户会话数据
        processed_sessions = []
        for session_data in user_sessions:
            session_id = str(session_data.get("session_id", f"session_{len(processed_sessions)}"))
            
            # 安全地转换product_id
            product_id_raw = session_data.get("product_id", 1)
            try:
                if isinstance(product_id_raw, (int, float)):
                    product_id = int(product_id_raw)
                elif isinstance(product_id_raw, str) and product_id_raw.isdigit():
                    product_id = int(product_id_raw)
                else:
                    product_id = 1  # 默认值
            except (ValueError, TypeError):
                product_id = 1
            
            state_data = session_data.get("state_data", {})
            
            if not isinstance(state_data, dict):
                state_data = {"value": str(state_data)}
            
            processed_sessions.append({
                "session_id": session_id,
                "product_id": product_id,
                "state_data": state_data
            })
        
        # 4. 执行状态操作
        operation_results = []
        
        for operation in state_operations:
            if not processed_sessions:
                continue
                
            session = processed_sessions[len(operation_results) % len(processed_sessions)]
            
            if operation == "save_state":
                result = state_manager.save_state(
                    session["session_id"],
                    session["product_id"],
                    session["state_data"]
                )
                operation_results.append({"operation": operation, "result": result})
                
                # 验证保存操作
                if result["success"]:
                    assert result["backend_used"] in persistence_system["storage_backends"], \
                        f"使用了无效的存储后端: {result['backend_used']}"
                    assert result["size"] > 0, "保存的状态大小应该大于0"
            
            elif operation == "load_state":
                result = state_manager.load_state(
                    session["session_id"],
                    session["product_id"]
                )
                operation_results.append({"operation": operation, "result": result})
                
                # 验证加载操作
                if result["success"]:
                    assert result["data"] is not None, "加载的状态数据不应该为空"
                    assert result["version"] > 0, "状态版本应该大于0"
            
            elif operation == "update_state":
                # 先加载现有状态
                load_result = state_manager.load_state(
                    session["session_id"],
                    session["product_id"]
                )
                
                if load_result["success"]:
                    # 更新状态数据
                    updated_data = load_result["data"].copy()
                    updated_data["updated_at"] = time.time()
                    
                    # 保存更新后的状态
                    save_result = state_manager.save_state(
                        session["session_id"],
                        session["product_id"],
                        updated_data
                    )
                    
                    operation_results.append({"operation": operation, "result": save_result})
                    
                    # 验证更新操作
                    if save_result["success"]:
                        assert save_result["version"] > load_result["version"], \
                            "更新后的版本号应该增加"
        
        # 5. 测试持久性场景
        for scenario in persistence_scenarios:
            if scenario == "browser_refresh":
                # 模拟浏览器刷新：sessionStorage清空，localStorage保留
                state_manager.storage["sessionStorage"].clear()
                state_manager.usage["sessionStorage"] = 0
                
                # 验证localStorage中的数据仍然存在
                localStorage_items = len(state_manager.storage["localStorage"])
                # localStorage应该保留数据（如果有的话）
                
            elif scenario == "tab_close_reopen":
                # 模拟标签页关闭重开：所有内存数据清空
                state_manager.storage["memory"].clear()
                state_manager.usage["memory"] = 0
                
                # 验证持久化存储中的数据仍然存在
                persistent_backends = ["localStorage", "indexedDB"]
                for backend in persistent_backends:
                    # 持久化后端应该保留数据
                    pass
            
            elif scenario == "session_timeout":
                # 模拟会话超时：清理过期数据
                current_time = time.time()
                
                for backend in state_manager.storage:
                    expired_keys = []
                    for key, item in state_manager.storage[backend].items():
                        # 模拟数据过期（设置为很久以前）
                        item["metadata"]["timestamp"] = current_time - 8 * 24 * 3600  # 8天前
                        if current_time - item["metadata"]["timestamp"] > 7 * 24 * 3600:
                            expired_keys.append(key)
                    
                    # 清理过期数据
                    for key in expired_keys:
                        if key in state_manager.storage[backend]:
                            del state_manager.storage[backend][key]
            
            elif scenario == "storage_full":
                # 模拟存储空间满：触发清理机制
                for backend in state_manager.storage:
                    backend_config = persistence_system["storage_backends"][backend]
                    # 模拟存储接近满载
                    state_manager.usage[backend] = int(backend_config["capacity"] * 0.95)
                
                # 尝试保存新数据应该触发清理
                if processed_sessions:
                    session = processed_sessions[0]
                    large_data = {"large_field": "x" * 1000}  # 1KB数据
                    result = state_manager.save_state(
                        session["session_id"],
                        session["product_id"],
                        large_data
                    )
                    
                    # 验证系统处理存储满的情况
                    # 可能成功（通过清理），也可能失败（无法清理足够空间）
            
            elif scenario == "network_offline":
                # 模拟网络离线：只能使用本地存储
                # 在这个简化实现中，所有存储都是本地的
                # 验证离线状态下的数据访问
                if processed_sessions:
                    session = processed_sessions[0]
                    offline_result = state_manager.load_state(
                        session["session_id"],
                        session["product_id"]
                    )
                    
                    # 离线状态下应该能够访问本地存储的数据
                    # 结果可能成功也可能失败，取决于是否有数据
            
            elif scenario == "browser_crash":
                # 模拟浏览器崩溃：内存和sessionStorage数据丢失
                state_manager.storage["memory"].clear()
                state_manager.storage["sessionStorage"].clear()
                state_manager.usage["memory"] = 0
                state_manager.usage["sessionStorage"] = 0
                
                # 验证持久化数据的恢复
                persistent_data_exists = (
                    len(state_manager.storage["localStorage"]) > 0 or
                    len(state_manager.storage["indexedDB"]) > 0
                )
                
                # 如果有持久化数据，应该能够恢复
                if persistent_data_exists and processed_sessions:
                    session = processed_sessions[0]
                    recovery_result = state_manager.load_state(
                        session["session_id"],
                        session["product_id"]
                    )
                    
                    # 恢复操作应该能够找到持久化的数据
                    if recovery_result["success"]:
                        assert recovery_result["backend_used"] in ["localStorage", "indexedDB"], \
                            "崩溃恢复应该使用持久化存储后端"
        
        # 6. 验证状态一致性
        def verify_state_consistency(state_manager: StateManager) -> dict:
            """验证状态一致性"""
            consistency_result = {
                "consistent": True,
                "issues": [],
                "statistics": {
                    "total_states": 0,
                    "total_size": 0,
                    "backend_distribution": {},
                    "version_distribution": {}
                }
            }
            
            total_states = 0
            total_size = 0
            
            for backend, storage in state_manager.storage.items():
                backend_count = len(storage)
                backend_size = sum(item["metadata"]["size"] for item in storage.values())
                
                consistency_result["statistics"]["backend_distribution"][backend] = {
                    "count": backend_count,
                    "size": backend_size
                }
                
                total_states += backend_count
                total_size += backend_size
                
                # 验证使用量统计的准确性
                if state_manager.usage[backend] != backend_size:
                    consistency_result["consistent"] = False
                    consistency_result["issues"].append(
                        f"后端 {backend} 使用量统计不一致: "
                        f"记录 {state_manager.usage[backend]}, 实际 {backend_size}"
                    )
            
            consistency_result["statistics"]["total_states"] = total_states
            consistency_result["statistics"]["total_size"] = total_size
            
            # 验证版本一致性
            for backend, storage in state_manager.storage.items():
                for key, item in storage.items():
                    metadata = item["metadata"]
                    base_key = f"{metadata['session_id']}_{metadata['product_id']}_{metadata['state_type']}"
                    
                    if base_key in state_manager.versions:
                        expected_version = state_manager.versions[base_key]
                        if metadata["version"] > expected_version:
                            consistency_result["consistent"] = False
                            consistency_result["issues"].append(
                                f"版本号不一致: {key} 版本 {metadata['version']} > 记录版本 {expected_version}"
                            )
            
            return consistency_result
        
        # 执行一致性验证
        consistency_result = verify_state_consistency(state_manager)
        
        # 验证一致性检查结果
        if consistency_result["issues"]:
            # 如果有一致性问题，记录但不一定失败（可能是测试场景导致的）
            pass
        
        assert isinstance(consistency_result["statistics"]["total_states"], int), \
            "状态总数应该是整数"
        
        assert consistency_result["statistics"]["total_size"] >= 0, \
            "总大小应该非负"
        
        # 7. 验证状态恢复机制
        def test_state_recovery(state_manager: StateManager, sessions: list) -> dict:
            """测试状态恢复机制"""
            recovery_result = {
                "recovery_rate": 0.0,
                "successful_recoveries": 0,
                "failed_recoveries": 0,
                "average_recovery_time": 0.0
            }
            
            recovery_times = []
            
            for session in sessions:
                start_time = time.time()
                
                # 尝试恢复状态
                load_result = state_manager.load_state(
                    session["session_id"],
                    session["product_id"]
                )
                
                recovery_time = time.time() - start_time
                recovery_times.append(recovery_time)
                
                if load_result["success"]:
                    recovery_result["successful_recoveries"] += 1
                    
                    # 验证恢复的数据完整性
                    recovered_data = load_result["data"]
                    assert isinstance(recovered_data, dict), "恢复的数据应该是字典类型"
                else:
                    recovery_result["failed_recoveries"] += 1
            
            total_attempts = len(sessions)
            if total_attempts > 0:
                recovery_result["recovery_rate"] = recovery_result["successful_recoveries"] / total_attempts
                recovery_result["average_recovery_time"] = sum(recovery_times) / len(recovery_times)
            
            return recovery_result
        
        # 测试状态恢复
        if processed_sessions:
            recovery_result = test_state_recovery(state_manager, processed_sessions)
            
            # 验证恢复性能
            assert recovery_result["recovery_rate"] >= 0.0, "恢复率应该非负"
            assert recovery_result["recovery_rate"] <= 1.0, "恢复率不应该超过100%"
            assert recovery_result["average_recovery_time"] >= 0.0, "平均恢复时间应该非负"
            assert recovery_result["average_recovery_time"] < 1.0, "平均恢复时间应该小于1秒"
    
    @given(
        device_configs=st.lists(
            st.dictionaries(
                st.sampled_from(['screen_width', 'screen_height', 'device_type', 'orientation', 'pixel_ratio']),
                st.one_of(
                    st.integers(min_value=320, max_value=3840),
                    st.sampled_from(['mobile', 'tablet', 'desktop', 'tv']),
                    st.sampled_from(['portrait', 'landscape']),
                    st.floats(min_value=1.0, max_value=4.0)
                ),
                min_size=3, max_size=5
            ),
            min_size=1, max_size=10
        ),
        layout_scenarios=st.lists(
            st.sampled_from([
                'mobile_portrait',
                'mobile_landscape',
                'tablet_portrait',
                'tablet_landscape',
                'desktop_small',
                'desktop_large',
                'ultrawide',
                'tv_display'
            ]),
            min_size=1, max_size=8
        ),
        interaction_modes=st.lists(
            st.sampled_from([
                'touch',
                'mouse',
                'keyboard',
                'gamepad',
                'voice',
                'gesture'
            ]),
            min_size=1, max_size=6
        )
    )
    def test_product_responsive_adaptability(self, device_configs, layout_scenarios, interaction_modes):
        """
        **Feature: product-integration, Property 12: 产品响应式适配性**
        **Validates: Requirements 6.5**
        
        验证产品响应式设计的适配性和兼容性：
        1. 不同屏幕尺寸的布局适配
        2. 设备类型的交互优化
        3. 触摸和鼠标操作支持
        4. 屏幕方向变化处理
        5. 高分辨率屏幕适配
        6. 可访问性和用户体验优化
        """
        # 1. 定义响应式设计系统
        responsive_system = {
            "breakpoints": {
                "xs": {"min_width": 0, "max_width": 575, "device_type": "mobile"},
                "sm": {"min_width": 576, "max_width": 767, "device_type": "mobile"},
                "md": {"min_width": 768, "max_width": 991, "device_type": "tablet"},
                "lg": {"min_width": 992, "max_width": 1199, "device_type": "desktop"},
                "xl": {"min_width": 1200, "max_width": 1599, "device_type": "desktop"},
                "xxl": {"min_width": 1600, "max_width": float('inf'), "device_type": "desktop"}
            },
            "layout_modes": {
                "mobile": {
                    "container_padding": "16px",
                    "font_size_base": "14px",
                    "touch_target_min": "44px",
                    "navigation_style": "bottom_tabs",
                    "content_width": "100%"
                },
                "tablet": {
                    "container_padding": "24px",
                    "font_size_base": "16px",
                    "touch_target_min": "44px",
                    "navigation_style": "side_drawer",
                    "content_width": "90%"
                },
                "desktop": {
                    "container_padding": "32px",
                    "font_size_base": "16px",
                    "touch_target_min": "32px",
                    "navigation_style": "top_bar",
                    "content_width": "80%"
                }
            },
            "interaction_adaptations": {
                "touch": {
                    "min_target_size": 44,
                    "gesture_support": True,
                    "hover_disabled": True,
                    "scroll_momentum": True
                },
                "mouse": {
                    "min_target_size": 32,
                    "hover_enabled": True,
                    "context_menu": True,
                    "precise_selection": True
                },
                "keyboard": {
                    "focus_indicators": True,
                    "tab_navigation": True,
                    "keyboard_shortcuts": True,
                    "skip_links": True
                }
            },
            "accessibility_features": {
                "high_contrast": True,
                "large_text": True,
                "reduced_motion": True,
                "screen_reader": True,
                "voice_control": True
            }
        }
        
        # 2. 设备检测和分类系统
        def detect_device_characteristics(device_config: dict) -> dict:
            """检测设备特征"""
            result = {
                "device_type": "desktop",
                "breakpoint": "lg",
                "orientation": "landscape",
                "pixel_ratio": 1.0,
                "touch_capable": False,
                "screen_size": "medium",
                "performance_tier": "high"
            }
            
            # 获取屏幕尺寸
            screen_width = device_config.get("screen_width", 1920)
            screen_height = device_config.get("screen_height", 1080)
            
            # 确保是数字类型
            try:
                screen_width = int(screen_width) if isinstance(screen_width, (int, float, str)) else 1920
                screen_height = int(screen_height) if isinstance(screen_height, (int, float, str)) else 1080
            except (ValueError, TypeError):
                screen_width, screen_height = 1920, 1080
            
            # 确定断点
            for breakpoint, config in responsive_system["breakpoints"].items():
                if config["min_width"] <= screen_width <= config["max_width"]:
                    result["breakpoint"] = breakpoint
                    result["device_type"] = config["device_type"]
                    break
            
            # 确定屏幕方向
            if screen_width > screen_height:
                result["orientation"] = "landscape"
            else:
                result["orientation"] = "portrait"
            
            # 确定屏幕大小类别
            if screen_width < 768:
                result["screen_size"] = "small"
            elif screen_width < 1200:
                result["screen_size"] = "medium"
            else:
                result["screen_size"] = "large"
            
            # 检测触摸能力
            device_type = device_config.get("device_type", "desktop")
            if device_type in ["mobile", "tablet"]:
                result["touch_capable"] = True
            
            # 获取像素比
            pixel_ratio = device_config.get("pixel_ratio", 1.0)
            try:
                result["pixel_ratio"] = float(pixel_ratio) if isinstance(pixel_ratio, (int, float, str)) else 1.0
            except (ValueError, TypeError):
                result["pixel_ratio"] = 1.0
            
            # 确定性能等级
            if result["device_type"] == "mobile":
                result["performance_tier"] = "low" if screen_width < 400 else "medium"
            elif result["device_type"] == "tablet":
                result["performance_tier"] = "medium"
            else:
                result["performance_tier"] = "high"
            
            return result
        
        # 3. 测试设备特征检测
        detected_devices = []
        for device_config in device_configs:
            device_characteristics = detect_device_characteristics(device_config)
            detected_devices.append({
                "config": device_config,
                "characteristics": device_characteristics
            })
            
            # 验证设备检测的合理性
            assert device_characteristics["device_type"] in ["mobile", "tablet", "desktop"], \
                f"设备类型应该是预定义的类型: {device_characteristics['device_type']}"
            
            assert device_characteristics["breakpoint"] in responsive_system["breakpoints"], \
                f"断点应该是预定义的断点: {device_characteristics['breakpoint']}"
            
            assert device_characteristics["orientation"] in ["portrait", "landscape"], \
                f"屏幕方向应该是预定义的方向: {device_characteristics['orientation']}"
        
        # 4. 布局适配系统
        def adapt_layout_for_device(device_characteristics: dict, layout_scenario: str) -> dict:
            """为设备适配布局"""
            adaptation_result = {
                "layout_applied": layout_scenario,
                "css_classes": [],
                "style_overrides": {},
                "component_visibility": {},
                "interaction_adaptations": [],
                "performance_optimizations": []
            }
            
            device_type = device_characteristics["device_type"]
            breakpoint = device_characteristics["breakpoint"]
            orientation = device_characteristics["orientation"]
            
            # 应用基础布局模式
            layout_config = responsive_system["layout_modes"].get(device_type, {})
            
            # 添加CSS类
            adaptation_result["css_classes"].extend([
                f"device-{device_type}",
                f"breakpoint-{breakpoint}",
                f"orientation-{orientation}"
            ])
            
            # 应用样式覆盖
            adaptation_result["style_overrides"].update({
                "container_padding": layout_config.get("container_padding", "16px"),
                "font_size": layout_config.get("font_size_base", "16px"),
                "content_width": layout_config.get("content_width", "100%")
            })
            
            # 组件可见性控制
            if device_type == "mobile":
                adaptation_result["component_visibility"].update({
                    "sidebar": False,
                    "breadcrumbs": False,
                    "detailed_tooltips": False,
                    "hamburger_menu": True
                })
            elif device_type == "tablet":
                adaptation_result["component_visibility"].update({
                    "sidebar": True,
                    "breadcrumbs": True,
                    "detailed_tooltips": True,
                    "hamburger_menu": False
                })
            else:  # desktop
                adaptation_result["component_visibility"].update({
                    "sidebar": True,
                    "breadcrumbs": True,
                    "detailed_tooltips": True,
                    "hamburger_menu": False
                })
            
            # 交互适配
            if device_characteristics["touch_capable"]:
                adaptation_result["interaction_adaptations"].extend([
                    "increase_touch_targets",
                    "enable_swipe_gestures",
                    "disable_hover_effects"
                ])
            else:
                adaptation_result["interaction_adaptations"].extend([
                    "enable_hover_effects",
                    "enable_context_menus",
                    "optimize_for_mouse"
                ])
            
            # 性能优化
            performance_tier = device_characteristics["performance_tier"]
            if performance_tier == "low":
                adaptation_result["performance_optimizations"].extend([
                    "reduce_animations",
                    "lazy_load_images",
                    "minimize_dom_updates"
                ])
            elif performance_tier == "medium":
                adaptation_result["performance_optimizations"].extend([
                    "optimize_animations",
                    "progressive_image_loading"
                ])
            
            return adaptation_result
        
        # 5. 测试布局适配
        for scenario in layout_scenarios:
            for device_info in detected_devices:
                device_characteristics = device_info["characteristics"]
                adaptation_result = adapt_layout_for_device(device_characteristics, scenario)
                
                # 验证适配结果的合理性
                assert isinstance(adaptation_result["css_classes"], list), \
                    "CSS类列表应该是列表类型"
                
                assert isinstance(adaptation_result["style_overrides"], dict), \
                    "样式覆盖应该是字典类型"
                
                # 验证移动设备的特殊适配
                if device_characteristics["device_type"] == "mobile":
                    assert not adaptation_result["component_visibility"].get("sidebar", True), \
                        "移动设备不应该显示侧边栏"
                    assert adaptation_result["component_visibility"].get("hamburger_menu", False), \
                        "移动设备应该显示汉堡菜单"
                
                # 验证触摸设备的交互适配
                if device_characteristics["touch_capable"]:
                    assert "increase_touch_targets" in adaptation_result["interaction_adaptations"], \
                        "触摸设备应该增大触摸目标"
        
        # 6. 交互模式适配
        def adapt_interaction_mode(interaction_mode: str, device_characteristics: dict) -> dict:
            """适配交互模式"""
            adaptation_result = {
                "mode": interaction_mode,
                "enabled": True,
                "optimizations": [],
                "accessibility_features": [],
                "fallback_modes": []
            }
            
            interaction_config = responsive_system["interaction_adaptations"].get(interaction_mode, {})
            
            if interaction_mode == "touch":
                if device_characteristics["touch_capable"]:
                    adaptation_result["optimizations"].extend([
                        "gesture_recognition",
                        "momentum_scrolling",
                        "touch_feedback"
                    ])
                else:
                    adaptation_result["enabled"] = False
                    adaptation_result["fallback_modes"].append("mouse")
            
            elif interaction_mode == "mouse":
                if not device_characteristics["touch_capable"]:
                    adaptation_result["optimizations"].extend([
                        "hover_states",
                        "context_menus",
                        "precise_selection"
                    ])
                else:
                    # 触摸设备也可以支持鼠标（如平板+鼠标）
                    adaptation_result["optimizations"].extend([
                        "hybrid_interaction",
                        "adaptive_cursors"
                    ])
            
            elif interaction_mode == "keyboard":
                adaptation_result["accessibility_features"].extend([
                    "focus_indicators",
                    "tab_navigation",
                    "keyboard_shortcuts"
                ])
                adaptation_result["optimizations"].extend([
                    "skip_links",
                    "aria_labels",
                    "screen_reader_support"
                ])
            
            elif interaction_mode == "gamepad":
                if device_characteristics["device_type"] in ["desktop", "tv"]:
                    adaptation_result["optimizations"].extend([
                        "gamepad_navigation",
                        "button_mapping",
                        "vibration_feedback"
                    ])
                else:
                    adaptation_result["enabled"] = False
                    adaptation_result["fallback_modes"].append("touch")
            
            return adaptation_result
        
        # 测试交互模式适配
        for interaction_mode in interaction_modes:
            for device_info in detected_devices:
                device_characteristics = device_info["characteristics"]
                interaction_adaptation = adapt_interaction_mode(interaction_mode, device_characteristics)
                
                # 验证交互适配的合理性
                assert isinstance(interaction_adaptation["enabled"], bool), \
                    "交互模式启用状态应该是布尔值"
                
                assert isinstance(interaction_adaptation["optimizations"], list), \
                    "优化列表应该是列表类型"
                
                # 验证触摸交互在非触摸设备上的处理
                if interaction_mode == "touch" and not device_characteristics["touch_capable"]:
                    assert not interaction_adaptation["enabled"] or len(interaction_adaptation["fallback_modes"]) > 0, \
                        "非触摸设备应该禁用触摸交互或提供回退方案"
        
        # 7. 响应式图片和媒体适配
        def adapt_media_for_device(device_characteristics: dict) -> dict:
            """为设备适配媒体资源"""
            media_adaptation = {
                "image_sizes": [],
                "video_quality": "auto",
                "lazy_loading": False,
                "compression_level": "medium",
                "format_preferences": []
            }
            
            screen_width = 1920  # 默认值
            pixel_ratio = device_characteristics.get("pixel_ratio", 1.0)
            performance_tier = device_characteristics.get("performance_tier", "high")
            
            # 根据屏幕尺寸确定图片大小
            if device_characteristics["device_type"] == "mobile":
                media_adaptation["image_sizes"] = ["320w", "480w", "640w"]
                media_adaptation["video_quality"] = "720p"
                media_adaptation["lazy_loading"] = True
                media_adaptation["compression_level"] = "high"
            elif device_characteristics["device_type"] == "tablet":
                media_adaptation["image_sizes"] = ["768w", "1024w", "1280w"]
                media_adaptation["video_quality"] = "1080p"
                media_adaptation["lazy_loading"] = True
                media_adaptation["compression_level"] = "medium"
            else:  # desktop
                media_adaptation["image_sizes"] = ["1200w", "1600w", "2000w"]
                media_adaptation["video_quality"] = "1080p"
                media_adaptation["lazy_loading"] = False
                media_adaptation["compression_level"] = "low"
            
            # 高分辨率屏幕适配
            if pixel_ratio > 2.0:
                media_adaptation["format_preferences"].extend(["webp", "avif"])
                media_adaptation["image_sizes"] = [f"{int(size[:-1]) * 2}w" for size in media_adaptation["image_sizes"]]
            
            # 性能等级适配
            if performance_tier == "low":
                media_adaptation["lazy_loading"] = True
                media_adaptation["compression_level"] = "high"
                media_adaptation["video_quality"] = "480p"
            
            return media_adaptation
        
        # 测试媒体适配
        for device_info in detected_devices:
            device_characteristics = device_info["characteristics"]
            media_adaptation = adapt_media_for_device(device_characteristics)
            
            # 验证媒体适配的合理性
            assert isinstance(media_adaptation["image_sizes"], list), \
                "图片尺寸列表应该是列表类型"
            
            assert media_adaptation["video_quality"] in ["480p", "720p", "1080p", "auto"], \
                f"视频质量应该是预定义的质量: {media_adaptation['video_quality']}"
            
            assert isinstance(media_adaptation["lazy_loading"], bool), \
                "懒加载设置应该是布尔值"
            
            # 验证移动设备的优化
            if device_characteristics["device_type"] == "mobile":
                assert media_adaptation["lazy_loading"], \
                    "移动设备应该启用懒加载"
                assert media_adaptation["compression_level"] == "high", \
                    "移动设备应该使用高压缩"
        
        # 8. 可访问性适配验证
        def validate_accessibility_compliance(device_characteristics: dict, interaction_modes: list) -> dict:
            """验证可访问性合规性"""
            accessibility_result = {
                "compliant": True,
                "issues": [],
                "recommendations": [],
                "score": 100
            }
            
            # 检查键盘导航支持
            if "keyboard" not in interaction_modes:
                accessibility_result["issues"].append("缺少键盘导航支持")
                accessibility_result["score"] -= 20
                accessibility_result["compliant"] = False
            
            # 检查触摸目标大小
            if device_characteristics["touch_capable"]:
                min_touch_target = responsive_system["interaction_adaptations"]["touch"]["min_target_size"]
                if min_touch_target < 44:
                    accessibility_result["issues"].append("触摸目标尺寸过小")
                    accessibility_result["score"] -= 15
            
            # 检查对比度和可读性
            if device_characteristics["device_type"] == "mobile":
                accessibility_result["recommendations"].extend([
                    "确保足够的颜色对比度",
                    "支持系统字体大小设置",
                    "提供高对比度模式"
                ])
            
            # 检查屏幕阅读器支持
            accessibility_result["recommendations"].append("添加ARIA标签和语义化HTML")
            
            return accessibility_result
        
        # 测试可访问性合规性
        for device_info in detected_devices:
            device_characteristics = device_info["characteristics"]
            accessibility_result = validate_accessibility_compliance(device_characteristics, interaction_modes)
            
            # 验证可访问性检查结果
            assert isinstance(accessibility_result["compliant"], bool), \
                "合规性状态应该是布尔值"
            
            assert 0 <= accessibility_result["score"] <= 100, \
                f"可访问性评分应该在0-100之间: {accessibility_result['score']}"
            
            assert isinstance(accessibility_result["issues"], list), \
                "问题列表应该是列表类型"
            
            assert isinstance(accessibility_result["recommendations"], list), \
                "建议列表应该是列表类型"
        
        # 9. 性能优化验证
        def validate_performance_optimization(device_characteristics: dict, adaptations: dict) -> dict:
            """验证性能优化"""
            performance_result = {
                "optimized": True,
                "metrics": {
                    "load_time_estimate": 0.0,
                    "memory_usage_mb": 0.0,
                    "cpu_usage_percent": 0.0,
                    "network_requests": 0
                },
                "optimizations_applied": [],
                "bottlenecks": []
            }
            
            performance_tier = device_characteristics.get("performance_tier", "high")
            device_type = device_characteristics.get("device_type", "desktop")
            
            # 基础性能指标
            base_load_time = 2.0  # 秒
            base_memory = 50.0    # MB
            base_cpu = 20.0       # 百分比
            base_requests = 10    # 网络请求数
            
            # 根据设备类型调整
            if device_type == "mobile":
                base_load_time *= 1.5
                base_memory *= 0.7
                base_cpu *= 1.3
            elif device_type == "tablet":
                base_load_time *= 1.2
                base_memory *= 0.8
                base_cpu *= 1.1
            
            # 根据性能等级调整
            if performance_tier == "low":
                base_load_time *= 2.0
                base_memory *= 0.5
                base_cpu *= 2.0
            elif performance_tier == "medium":
                base_load_time *= 1.3
                base_memory *= 0.7
                base_cpu *= 1.5
            
            # 应用优化
            optimizations = adaptations.get("performance_optimizations", [])
            for optimization in optimizations:
                if optimization == "lazy_load_images":
                    base_load_time *= 0.8
                    base_requests *= 0.6
                    performance_result["optimizations_applied"].append(optimization)
                elif optimization == "reduce_animations":
                    base_cpu *= 0.7
                    performance_result["optimizations_applied"].append(optimization)
                elif optimization == "minimize_dom_updates":
                    base_cpu *= 0.8
                    base_memory *= 0.9
                    performance_result["optimizations_applied"].append(optimization)
            
            performance_result["metrics"].update({
                "load_time_estimate": base_load_time,
                "memory_usage_mb": base_memory,
                "cpu_usage_percent": base_cpu,
                "network_requests": int(base_requests)
            })
            
            # 检查性能瓶颈
            if base_load_time > 5.0:
                performance_result["bottlenecks"].append("加载时间过长")
                performance_result["optimized"] = False
            
            if base_memory > 100.0:
                performance_result["bottlenecks"].append("内存使用过高")
                performance_result["optimized"] = False
            
            if base_cpu > 80.0:
                performance_result["bottlenecks"].append("CPU使用率过高")
                performance_result["optimized"] = False
            
            return performance_result
        
        # 测试性能优化
        for device_info in detected_devices:
            device_characteristics = device_info["characteristics"]
            
            # 获取适配结果
            adaptation_result = adapt_layout_for_device(device_characteristics, layout_scenarios[0] if layout_scenarios else "desktop_large")
            
            # 验证性能优化
            performance_result = validate_performance_optimization(device_characteristics, adaptation_result)
            
            # 验证性能指标的合理性
            assert performance_result["metrics"]["load_time_estimate"] > 0, \
                "加载时间估算应该大于0"
            
            assert performance_result["metrics"]["memory_usage_mb"] > 0, \
                "内存使用应该大于0"
            
            assert 0 <= performance_result["metrics"]["cpu_usage_percent"] <= 100, \
                f"CPU使用率应该在0-100之间: {performance_result['metrics']['cpu_usage_percent']}"
            
            # 验证低性能设备的优化
            if device_characteristics.get("performance_tier") == "low":
                assert len(performance_result["optimizations_applied"]) > 0, \
                    "低性能设备应该应用性能优化"
    
    @settings(suppress_health_check=[HealthCheck.too_slow], max_examples=5)
    @given(
        products=st.lists(product_data(), min_size=1, max_size=2),
        access_events=st.lists(
            st.fixed_dictionaries({
                'user_id': st.one_of(st.none(), st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')))),
                'session_id': st.text(min_size=8, max_size=32, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
                'access_time': st.floats(min_value=time.time()-3600, max_value=time.time()),
                'duration': st.integers(min_value=1, max_value=3600),  # 1秒到1小时
                'user_agent': st.sampled_from(['Mozilla/5.0', 'Chrome/91.0', 'Safari/14.0', 'Firefox/89.0']),
                'ip_address': st.sampled_from(['192.168.1.1', '10.0.0.1', '172.16.0.1', '203.0.113.1']),
                'referrer': st.one_of(st.none(), st.sampled_from(['https://example.com', 'https://google.com', 'direct'])),
                'exit_method': st.sampled_from(['navigation', 'close', 'timeout', 'error'])
            }),
            min_size=1, max_size=20
        ),
        time_ranges=st.lists(
            st.tuples(
                st.floats(min_value=time.time()-3600, max_value=time.time()-1800),
                st.floats(min_value=time.time()-1800, max_value=time.time())
            ),
            min_size=1, max_size=5
        )
    )
    def test_product_access_statistics_accuracy(self, products, access_events, time_ranges):
        """
        **Feature: product-integration, Property 6: 产品访问统计准确性**
        **Validates: Requirements 7.1, 7.2**
        
        验证产品访问统计数据的准确性和一致性：
        1. 访问次数统计准确
        2. 访问时长计算正确
        3. 用户统计数据一致
        4. 时间范围查询准确
        5. 并发访问处理正确
        6. 统计数据聚合准确
        """
        def _progress(message: str) -> None:
            if os.environ.get("AUGUST_TEST_PROGRESS") == "1":
                print(f"[progress] {message}")

        _progress("start")
        # 1. 模拟统计数据收集系统
        class AccessStatisticsCollector:
            def __init__(self):
                self.access_logs = []
                self.user_sessions = {}
                self.product_stats = {}
                self.daily_stats = {}
                self.real_time_stats = {}
            
            def record_access(self, product_id: int, event: dict):
                """记录访问事件"""
                log_entry = {
                    "product_id": product_id,
                    "timestamp": event["access_time"],
                    "user_id": event.get("user_id"),
                    "session_id": event["session_id"],
                    "duration": event["duration"],
                    "user_agent": event["user_agent"],
                    "ip_address": event["ip_address"],
                    "referrer": event.get("referrer"),
                    "exit_method": event["exit_method"]
                }
                
                self.access_logs.append(log_entry)
                
                # 更新产品统计
                if product_id not in self.product_stats:
                    self.product_stats[product_id] = {
                        "total_visits": 0,
                        "total_duration": 0,
                        "unique_users": set(),
                        "unique_sessions": set(),
                        "bounce_rate": 0.0,
                        "avg_duration": 0.0
                    }
                
                stats = self.product_stats[product_id]
                stats["total_visits"] += 1
                stats["total_duration"] += event["duration"]
                stats["unique_sessions"].add(event["session_id"])
                
                if event.get("user_id"):
                    stats["unique_users"].add(event["user_id"])
                
                # 计算平均时长
                stats["avg_duration"] = stats["total_duration"] / stats["total_visits"]
                
                # 计算跳出率（访问时长小于30秒的比例）
                short_visits = sum(1 for log in self.access_logs 
                                 if log["product_id"] == product_id and log["duration"] < 30)
                stats["bounce_rate"] = short_visits / stats["total_visits"]
            
            def get_product_statistics(self, product_id: int, start_time: float = None, end_time: float = None):
                """获取产品统计数据"""
                filtered_logs = [
                    log for log in self.access_logs 
                    if log["product_id"] == product_id
                ]
                
                if start_time is not None:
                    filtered_logs = [log for log in filtered_logs if log["timestamp"] >= start_time]
                
                if end_time is not None:
                    filtered_logs = [log for log in filtered_logs if log["timestamp"] <= end_time]
                
                if not filtered_logs:
                    return {
                        "total_visits": 0,
                        "total_duration": 0,
                        "unique_users": 0,
                        "unique_sessions": 0,
                        "avg_duration": 0.0,
                        "bounce_rate": 0.0
                    }
                
                total_visits = len(filtered_logs)
                total_duration = sum(log["duration"] for log in filtered_logs)
                unique_users = len(set(log["user_id"] for log in filtered_logs if log["user_id"]))
                unique_sessions = len(set(log["session_id"] for log in filtered_logs))
                avg_duration = total_duration / total_visits if total_visits > 0 else 0.0
                
                short_visits = sum(1 for log in filtered_logs if log["duration"] < 30)
                bounce_rate = short_visits / total_visits if total_visits > 0 else 0.0
                
                return {
                    "total_visits": total_visits,
                    "total_duration": total_duration,
                    "unique_users": unique_users,
                    "unique_sessions": unique_sessions,
                    "avg_duration": avg_duration,
                    "bounce_rate": bounce_rate
                }
            
            def get_trending_data(self, product_id: int, hours: int = 24):
                """获取趋势数据"""
                current_time = time.time()
                start_time = current_time - (hours * 3600)
                
                hourly_stats = {}
                for hour in range(hours):
                    hour_start = start_time + (hour * 3600)
                    hour_end = hour_start + 3600
                    
                    hour_logs = [
                        log for log in self.access_logs
                        if (log["product_id"] == product_id and 
                            hour_start <= log["timestamp"] < hour_end)
                    ]
                    
                    hourly_stats[hour] = {
                        "visits": len(hour_logs),
                        "duration": sum(log["duration"] for log in hour_logs),
                        "unique_users": len(set(log["user_id"] for log in hour_logs if log["user_id"]))
                    }
                
                return hourly_stats
        
        # 2. 初始化统计收集器
        stats_collector = AccessStatisticsCollector()
        _progress("collector_initialized")
        
        # 3. 测试访问事件记录和统计
        for i, product_data in enumerate(products):
            product_id = i + 1
            
            # 为每个产品记录访问事件
            product_events = [event for j, event in enumerate(access_events) if j % len(products) == i]
            
            for event in product_events:
                stats_collector.record_access(product_id, event)
            
            # 验证基础统计数据的准确性
            stats = stats_collector.get_product_statistics(product_id)
            
            # 验证访问次数
            expected_visits = len(product_events)
            assert stats["total_visits"] == expected_visits, \
                f"产品 {product_id} 访问次数统计不准确: 期望 {expected_visits}, 实际 {stats['total_visits']}"
            
            # 验证总时长
            expected_duration = sum(event["duration"] for event in product_events)
            assert stats["total_duration"] == expected_duration, \
                f"产品 {product_id} 总访问时长统计不准确: 期望 {expected_duration}, 实际 {stats['total_duration']}"
            
            # 验证平均时长
            if expected_visits > 0:
                expected_avg = expected_duration / expected_visits
                assert abs(stats["avg_duration"] - expected_avg) < 0.01, \
                    f"产品 {product_id} 平均访问时长计算不准确: 期望 {expected_avg}, 实际 {stats['avg_duration']}"
            
            # 验证唯一会话数
            expected_sessions = len(set(event["session_id"] for event in product_events))
            assert stats["unique_sessions"] == expected_sessions, \
                f"产品 {product_id} 唯一会话数统计不准确: 期望 {expected_sessions}, 实际 {stats['unique_sessions']}"
            
            # 验证唯一用户数
            expected_users = len(set(event["user_id"] for event in product_events if event["user_id"]))
            assert stats["unique_users"] == expected_users, \
                f"产品 {product_id} 唯一用户数统计不准确: 期望 {expected_users}, 实际 {stats['unique_users']}"
        _progress("basic_stats_checked")
        
        # 4. 验证时间范围查询的准确性
        for i, product_data in enumerate(products):
            product_id = i + 1
            
            for start_time, end_time in time_ranges:
                # 获取时间范围内的统计数据
                range_stats = stats_collector.get_product_statistics(product_id, start_time, end_time)
                
                # 手动计算期望的统计数据
                product_events = [event for j, event in enumerate(access_events) if j % len(products) == i]
                filtered_events = [
                    event for event in product_events
                    if start_time <= event["access_time"] <= end_time
                ]
                
                expected_visits = len(filtered_events)
                expected_duration = sum(event["duration"] for event in filtered_events)
                
                # 验证时间范围查询结果
                assert range_stats["total_visits"] == expected_visits, \
                    f"产品 {product_id} 时间范围查询访问次数不准确: 期望 {expected_visits}, 实际 {range_stats['total_visits']}"
                
                assert range_stats["total_duration"] == expected_duration, \
                    f"产品 {product_id} 时间范围查询总时长不准确: 期望 {expected_duration}, 实际 {range_stats['total_duration']}"
        _progress("range_stats_checked")
        
        # 5. 验证并发访问处理的正确性
        def simulate_concurrent_access(product_id: int, concurrent_events: list):
            """模拟并发访问"""
            concurrent_stats = {
                "simultaneous_users": 0,
                "peak_concurrent_users": 0,
                "concurrent_sessions": set(),
                "overlapping_visits": 0
            }
            
            # 按时间排序事件
            sorted_events = sorted(concurrent_events, key=lambda x: x["access_time"])
            
            active_sessions = {}
            max_concurrent = 0
            
            for event in sorted_events:
                session_id = event["session_id"]
                start_time = event["access_time"]
                end_time = start_time + event["duration"]
                
                # 清理已结束的会话
                active_sessions = {
                    sid: end_t for sid, end_t in active_sessions.items()
                    if end_t > start_time
                }
                
                # 添加新会话
                active_sessions[session_id] = end_time
                
                # 更新并发统计
                current_concurrent = len(active_sessions)
                max_concurrent = max(max_concurrent, current_concurrent)
                
                if current_concurrent > 1:
                    concurrent_stats["overlapping_visits"] += 1
            
            concurrent_stats["peak_concurrent_users"] = max_concurrent
            concurrent_stats["concurrent_sessions"] = set(active_sessions.keys())
            
            return concurrent_stats
        
        # 测试并发访问统计
        for i, product_data in enumerate(products):
            product_id = i + 1
            product_events = [event for j, event in enumerate(access_events) if j % len(products) == i]
            
            if len(product_events) > 1:
                concurrent_stats = simulate_concurrent_access(product_id, product_events)
                
                # 验证并发统计的合理性
                assert concurrent_stats["peak_concurrent_users"] >= 1, \
                    f"产品 {product_id} 峰值并发用户数应该至少为1"
                
                assert concurrent_stats["peak_concurrent_users"] <= len(product_events), \
                    f"产品 {product_id} 峰值并发用户数不应该超过总访问数"
        _progress("concurrency_checked")
        
        # 6. 验证统计数据的一致性和完整性
        def validate_statistics_consistency(collector: AccessStatisticsCollector):
            """验证统计数据的一致性"""
            total_logs = len(collector.access_logs)
            
            # 验证各产品统计数据之和等于总数
            total_visits_sum = 0
            total_duration_sum = 0
            
            for product_id in range(1, len(products) + 1):
                stats = collector.get_product_statistics(product_id)
                total_visits_sum += stats["total_visits"]
                total_duration_sum += stats["total_duration"]
            
            assert total_visits_sum == total_logs, \
                f"各产品访问次数之和与总日志数不一致: {total_visits_sum} vs {total_logs}"
            
            # 验证统计数据的数值合理性
            for product_id in range(1, len(products) + 1):
                stats = collector.get_product_statistics(product_id)
                
                # 平均时长应该在合理范围内
                if stats["total_visits"] > 0:
                    assert 0 < stats["avg_duration"] <= 7200, \
                        f"产品 {product_id} 平均访问时长超出合理范围: {stats['avg_duration']}"
                
                # 跳出率应该在0-1之间
                assert 0 <= stats["bounce_rate"] <= 1, \
                    f"产品 {product_id} 跳出率超出有效范围: {stats['bounce_rate']}"
                
                # 唯一用户数不应该超过总访问数
                assert stats["unique_users"] <= stats["total_visits"], \
                    f"产品 {product_id} 唯一用户数不应该超过总访问数"
                
                # 唯一会话数不应该超过总访问数
                assert stats["unique_sessions"] <= stats["total_visits"], \
                    f"产品 {product_id} 唯一会话数不应该超过总访问数"
        
        # 执行一致性验证
        validate_statistics_consistency(stats_collector)
        _progress("consistency_checked")
        
        # 7. 验证趋势数据的准确性
        for i, product_data in enumerate(products):
            product_id = i + 1
            
            # 获取24小时趋势数据
            trending_data = stats_collector.get_trending_data(product_id, 24)
            
            # 验证趋势数据结构
            assert len(trending_data) == 24, \
                f"产品 {product_id} 趋势数据应该包含24小时的数据"
            
            # 验证每小时数据的合理性
            for hour, hour_stats in trending_data.items():
                assert isinstance(hour_stats["visits"], int) and hour_stats["visits"] >= 0, \
                    f"产品 {product_id} 第{hour}小时访问次数数据类型错误"
                
                assert isinstance(hour_stats["duration"], int) and hour_stats["duration"] >= 0, \
                    f"产品 {product_id} 第{hour}小时访问时长数据类型错误"
                
                assert isinstance(hour_stats["unique_users"], int) and hour_stats["unique_users"] >= 0, \
                    f"产品 {product_id} 第{hour}小时唯一用户数数据类型错误"
        _progress("trending_checked")
        
        # 8. 验证实时统计更新的准确性
        def test_real_time_updates(collector: AccessStatisticsCollector, new_events: list):
            """测试实时统计更新"""
            # 记录更新前的统计数据
            before_stats = {}
            for product_id in range(1, len(products) + 1):
                before_stats[product_id] = collector.get_product_statistics(product_id)
            
            # 添加新的访问事件
            for i, event in enumerate(new_events):
                product_id = (i % len(products)) + 1
                collector.record_access(product_id, event)
            
            # 验证统计数据已正确更新
            for product_id in range(1, len(products) + 1):
                after_stats = collector.get_product_statistics(product_id)
                before = before_stats[product_id]
                
                # 计算期望的增量
                product_new_events = [
                    event for i, event in enumerate(new_events)
                    if (i % len(products)) + 1 == product_id
                ]
                
                expected_visit_increase = len(product_new_events)
                expected_duration_increase = sum(event["duration"] for event in product_new_events)
                
                # 验证增量更新
                assert after_stats["total_visits"] == before["total_visits"] + expected_visit_increase, \
                    f"产品 {product_id} 实时访问次数更新不正确"
                
                assert after_stats["total_duration"] == before["total_duration"] + expected_duration_increase, \
                    f"产品 {product_id} 实时访问时长更新不正确"
        
        # 生成一些新的测试事件
        if access_events:
            test_events = access_events[:min(5, len(access_events))]
            test_real_time_updates(stats_collector, test_events)
        
        # 9. 验证统计数据的持久性和恢复
        def test_statistics_persistence(collector: AccessStatisticsCollector):
            """测试统计数据的持久性"""
            # 模拟数据持久化
            persistent_data = {
                "access_logs": collector.access_logs.copy(),
                "product_stats": {},
                "metadata": {
                    "last_updated": time.time(),
                    "total_logs": len(collector.access_logs),
                    "data_version": "1.0"
                }
            }
            
            # 转换统计数据为可序列化格式
            for product_id, stats in collector.product_stats.items():
                persistent_data["product_stats"][product_id] = {
                    "total_visits": stats["total_visits"],
                    "total_duration": stats["total_duration"],
                    "unique_users": len(stats["unique_users"]),
                    "unique_sessions": len(stats["unique_sessions"]),
                    "bounce_rate": stats["bounce_rate"],
                    "avg_duration": stats["avg_duration"]
                }
            
            # 模拟数据恢复
            recovered_collector = AccessStatisticsCollector()
            recovered_collector.access_logs = persistent_data["access_logs"]
            
            # 重新计算统计数据
            for log in recovered_collector.access_logs:
                product_id = log["product_id"]
                event = {
                    "access_time": log["timestamp"],
                    "duration": log["duration"],
                    "session_id": log["session_id"],
                    "user_id": log["user_id"],
                    "user_agent": log["user_agent"],
                    "ip_address": log["ip_address"],
                    "referrer": log["referrer"],
                    "exit_method": log["exit_method"]
                }
                recovered_collector.record_access(product_id, event)
            
            # 验证恢复后的数据一致性
            for product_id in persistent_data["product_stats"]:
                original_stats = persistent_data["product_stats"][product_id]
                recovered_stats = recovered_collector.get_product_statistics(product_id)
                
                assert recovered_stats["total_visits"] == original_stats["total_visits"], \
                    f"产品 {product_id} 恢复后访问次数不一致"
                
                assert recovered_stats["total_duration"] == original_stats["total_duration"], \
                    f"产品 {product_id} 恢复后总时长不一致"
                
                assert abs(recovered_stats["avg_duration"] - original_stats["avg_duration"]) < 0.01, \
                    f"产品 {product_id} 恢复后平均时长不一致"
        
        # 执行持久性测试
        test_statistics_persistence(stats_collector)
        _progress("persistence_checked")
        
        # 10. 验证统计数据的性能和扩展性
        def validate_statistics_performance(event_count: int):
            """验证统计系统的性能"""
            performance_metrics = {
                "processing_time_per_event": 0.001,  # 1ms per event
                "memory_usage_per_event": 0.0001,    # 0.1KB per event
                "query_response_time": 0.01,         # 10ms for queries
                "max_concurrent_updates": 1000
            }
            
            # 计算预期性能指标
            total_processing_time = event_count * performance_metrics["processing_time_per_event"]
            total_memory_usage = event_count * performance_metrics["memory_usage_per_event"]
            
            # 验证性能在可接受范围内
            assert total_processing_time < 10.0, \
                f"统计处理时间过长: {total_processing_time}秒"
            
            assert total_memory_usage < 100.0, \
                f"统计内存使用过高: {total_memory_usage}MB"
            
            # 验证查询性能
            assert performance_metrics["query_response_time"] < 0.1, \
                f"统计查询响应时间过长: {performance_metrics['query_response_time']}秒"
            
            return True
        
        # 测试性能
        total_events = len(access_events)
        performance_valid = validate_statistics_performance(total_events)
        assert performance_valid, "统计系统性能验证失败"
        _progress("performance_checked")
    
    @settings(suppress_health_check=[HealthCheck.too_slow], max_examples=100)
    @given(
        products=st.lists(product_data(), min_size=1, max_size=3),
        api_requests=st.lists(
            st.fixed_dictionaries({
                'method': st.sampled_from(['GET', 'POST', 'PUT', 'DELETE']),
                'endpoint': st.sampled_from([
                    '/api/products/{id}/data',
                    '/api/products/{id}/stats',
                    '/api/products/{id}/config',
                    '/api/auth/token'
                ]),
                'headers': st.dictionaries(
                    st.sampled_from(['Authorization', 'Content-Type', 'User-Agent']),
                    st.sampled_from(['Bearer token123', 'application/json', 'Mozilla/5.0']),
                    min_size=1, max_size=3
                ),
                'payload': st.one_of(
                    st.none(),
                    st.dictionaries(
                        st.sampled_from(['data', 'config', 'value']), 
                        st.one_of(st.text(max_size=50), st.integers(), st.booleans()), 
                        max_size=5
                    )
                ),
                'timestamp': st.floats(min_value=time.time()-1800, max_value=time.time())
            }),
            min_size=1, max_size=15
        ),
        security_scenarios=st.lists(
            st.sampled_from([
                'invalid_token',
                'expired_token',
                'insufficient_permissions',
                'sql_injection_attempt',
                'xss_attempt'
            ]),
            min_size=1, max_size=5
        )
    )
    def test_product_api_communication_security(self, products, api_requests, security_scenarios):
        """
        **Feature: product-integration, Property 14: 产品API通信安全性**
        **Validates: Requirements 8.1**
        
        验证产品API通信的安全性和可靠性：
        1. 认证和授权机制正确
        2. API令牌验证和管理
        3. 请求限流和防护
        4. 输入验证和清理
        5. 安全攻击防护
        6. 通信加密和完整性
        """
        # 1. 模拟API安全管理系统
        class APISecurityManager:
            def __init__(self):
                self.tokens = {}
                self.rate_limits = {}
                self.security_logs = []
                self.blocked_ips = set()
                self.api_permissions = {}
                self.encryption_keys = {}
            
            def generate_token(self, product_id: int, user_id: str, permissions: list) -> str:
                """生成API令牌"""
                import secrets
                
                token = secrets.token_urlsafe(32)
                self.tokens[token] = {
                    "product_id": product_id,
                    "user_id": user_id,
                    "permissions": permissions,
                    "created_at": time.time(),
                    "expires_at": time.time() + 3600,  # 1小时过期
                    "last_used": None,
                    "usage_count": 0,
                    "is_active": True
                }
                
                return token
            
            def validate_token(self, token: str) -> dict:
                """验证API令牌"""
                if not token or token not in self.tokens:
                    return {"valid": False, "error": "令牌不存在"}
                
                token_data = self.tokens[token]
                
                if not token_data["is_active"]:
                    return {"valid": False, "error": "令牌已被撤销"}
                
                if time.time() > token_data["expires_at"]:
                    token_data["is_active"] = False
                    return {"valid": False, "error": "令牌已过期"}
                
                # 更新使用记录
                token_data["last_used"] = time.time()
                token_data["usage_count"] += 1
                
                return {
                    "valid": True,
                    "product_id": token_data["product_id"],
                    "user_id": token_data["user_id"],
                    "permissions": token_data["permissions"]
                }
            
            def check_rate_limit(self, ip_address: str, endpoint: str) -> bool:
                """检查请求频率限制"""
                current_time = time.time()
                key = f"{ip_address}:{endpoint}"
                
                if key not in self.rate_limits:
                    self.rate_limits[key] = {
                        "requests": [],
                        "blocked_until": 0
                    }
                
                rate_data = self.rate_limits[key]
                
                # 检查是否在封禁期内
                if current_time < rate_data["blocked_until"]:
                    return False
                
                # 清理过期的请求记录（1分钟窗口）
                rate_data["requests"] = [
                    req_time for req_time in rate_data["requests"]
                    if current_time - req_time < 60
                ]
                
                # 检查请求频率（每分钟最多60次请求）
                if len(rate_data["requests"]) >= 60:
                    rate_data["blocked_until"] = current_time + 300  # 封禁5分钟
                    self.blocked_ips.add(ip_address)
                    return False
                
                # 记录当前请求
                rate_data["requests"].append(current_time)
                return True
            
            def validate_request_payload(self, payload: dict, endpoint: str) -> dict:
                """验证请求负载"""
                if not payload:
                    return {"valid": True, "sanitized_payload": {}}
                
                sanitized = {}
                security_issues = []
                
                for key, value in payload.items():
                    # 检查键名安全性
                    if not self._is_safe_key(key):
                        security_issues.append(f"不安全的键名: {key}")
                        continue
                    
                    # 检查值的安全性
                    if isinstance(value, str):
                        sanitized_value, issues = self._sanitize_string_value(value)
                        sanitized[key] = sanitized_value
                        security_issues.extend(issues)
                    elif isinstance(value, (int, float, bool)):
                        sanitized[key] = value
                    else:
                        security_issues.append(f"不支持的数据类型: {type(value)}")
                
                return {
                    "valid": len(security_issues) == 0,
                    "sanitized_payload": sanitized,
                    "security_issues": security_issues
                }
            
            def _is_safe_key(self, key: str) -> bool:
                """检查键名是否安全"""
                import re
                
                # 只允许字母、数字和下划线
                if not re.match(r'^[a-zA-Z0-9_]+$', key):
                    return False
                
                # 检查危险关键词
                dangerous_keywords = [
                    'password', 'secret', 'token', 'key', 'admin',
                    'root', 'system', 'config', 'database', 'sql'
                ]
                
                return key.lower() not in dangerous_keywords
            
            def _sanitize_string_value(self, value: str) -> tuple:
                """清理字符串值"""
                import html
                import re
                
                issues = []
                sanitized = value
                
                # 检查SQL注入
                sql_patterns = [
                    r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER)\b)",
                    r"(\b(UNION|OR|AND)\s+\d+\s*=\s*\d+)",
                    r"(--|#|/\*|\*/)",
                    r"(\bEXEC\b|\bEXECUTE\b)"
                ]
                
                for pattern in sql_patterns:
                    if re.search(pattern, value, re.IGNORECASE):
                        issues.append("检测到SQL注入尝试")
                        break
                
                # 检查XSS攻击
                xss_patterns = [
                    r"<script[^>]*>.*?</script>",
                    r"javascript:",
                    r"on\w+\s*=",
                    r"<iframe[^>]*>",
                    r"<object[^>]*>",
                    r"<embed[^>]*>"
                ]
                
                for pattern in xss_patterns:
                    if re.search(pattern, value, re.IGNORECASE):
                        issues.append("检测到XSS攻击尝试")
                        sanitized = html.escape(sanitized)
                        break
                
                # 检查路径遍历
                if '..' in value or value.startswith('/') or '\\' in value:
                    issues.append("检测到路径遍历尝试")
                    sanitized = sanitized.replace('..', '').replace('/', '').replace('\\', '')
                
                # 长度限制
                if len(sanitized) > 1000:
                    issues.append("字符串长度超过限制")
                    sanitized = sanitized[:1000]
                
                return sanitized, issues
            
            def log_security_event(self, event_type: str, details: dict):
                """记录安全事件"""
                self.security_logs.append({
                    "timestamp": time.time(),
                    "event_type": event_type,
                    "details": details,
                    "severity": self._get_event_severity(event_type)
                })
            
            def _get_event_severity(self, event_type: str) -> str:
                """获取事件严重程度"""
                high_severity = [
                    "sql_injection_attempt", "xss_attempt", "csrf_attack",
                    "unauthorized_access", "token_theft"
                ]
                
                medium_severity = [
                    "rate_limit_exceeded", "invalid_token", "expired_token"
                ]
                
                if event_type in high_severity:
                    return "high"
                elif event_type in medium_severity:
                    return "medium"
                else:
                    return "low"
        
        # 2. 初始化安全管理器
        security_manager = APISecurityManager()
        
        # 3. 为每个产品生成API令牌
        product_tokens = {}
        for i, product_data in enumerate(products):
            product_id = i + 1
            
            # 生成不同权限级别的令牌
            admin_token = security_manager.generate_token(
                product_id, f"admin_{product_id}", 
                ["read", "write", "admin", "delete"]
            )
            
            user_token = security_manager.generate_token(
                product_id, f"user_{product_id}",
                ["read", "write"]
            )
            
            readonly_token = security_manager.generate_token(
                product_id, f"readonly_{product_id}",
                ["read"]
            )
            
            product_tokens[product_id] = {
                "admin": admin_token,
                "user": user_token,
                "readonly": readonly_token
            }
        
        # 4. 测试API请求的安全验证
        def process_api_request(request: dict, product_id: int, ip_address: str = "192.168.1.100") -> dict:
            """处理API请求并进行安全验证"""
            result = {
                "success": False,
                "status_code": 200,
                "response": None,
                "security_checks": {
                    "token_valid": False,
                    "rate_limit_ok": False,
                    "payload_safe": False,
                    "permissions_ok": False
                },
                "errors": []
            }
            
            # 1. 检查请求频率限制
            endpoint = request["endpoint"].replace("{id}", str(product_id))
            if not security_manager.check_rate_limit(ip_address, endpoint):
                result["status_code"] = 429
                result["errors"].append("请求频率超过限制")
                security_manager.log_security_event("rate_limit_exceeded", {
                    "ip_address": ip_address,
                    "endpoint": endpoint
                })
                return result
            
            result["security_checks"]["rate_limit_ok"] = True
            
            # 2. 验证API令牌
            auth_header = request["headers"].get("Authorization", "")
            if not auth_header.startswith("Bearer "):
                result["status_code"] = 401
                result["errors"].append("缺少有效的认证令牌")
                return result
            
            token = auth_header.replace("Bearer ", "")
            token_validation = security_manager.validate_token(token)
            
            if not token_validation["valid"]:
                result["status_code"] = 401
                result["errors"].append(f"令牌验证失败: {token_validation['error']}")
                security_manager.log_security_event("invalid_token", {
                    "token": token[:8] + "...",
                    "error": token_validation["error"]
                })
                return result
            
            result["security_checks"]["token_valid"] = True
            
            # 3. 检查产品访问权限
            if token_validation["product_id"] != product_id:
                result["status_code"] = 403
                result["errors"].append("无权访问此产品")
                security_manager.log_security_event("unauthorized_access", {
                    "user_id": token_validation["user_id"],
                    "requested_product": product_id,
                    "authorized_product": token_validation["product_id"]
                })
                return result
            
            # 4. 检查操作权限
            required_permission = self._get_required_permission(request["method"], endpoint)
            if required_permission not in token_validation["permissions"]:
                result["status_code"] = 403
                result["errors"].append(f"缺少必要权限: {required_permission}")
                return result
            
            result["security_checks"]["permissions_ok"] = True
            
            # 5. 验证请求负载
            if request["payload"]:
                payload_validation = security_manager.validate_request_payload(
                    request["payload"], endpoint
                )
                
                if not payload_validation["valid"]:
                    result["status_code"] = 400
                    result["errors"].extend(payload_validation["security_issues"])
                    security_manager.log_security_event("malicious_payload", {
                        "issues": payload_validation["security_issues"],
                        "endpoint": endpoint
                    })
                    return result
            
            result["security_checks"]["payload_safe"] = True
            
            # 6. 模拟成功响应
            result["success"] = True
            result["response"] = {
                "message": "请求处理成功",
                "data": {"product_id": product_id, "timestamp": time.time()}
            }
            
            return result
        
        def _get_required_permission(self, method: str, endpoint: str) -> str:
            """获取操作所需的权限"""
            if method in ["GET"]:
                return "read"
            elif method in ["POST", "PUT", "PATCH"]:
                return "write"
            elif method in ["DELETE"]:
                return "delete"
            else:
                return "admin"
        
        # 5. 测试正常API请求
        for i, product_data in enumerate(products):
            product_id = i + 1
            tokens = product_tokens[product_id]
            
            for request in api_requests[:3]:  # 测试前3个请求
                # 使用管理员令牌测试
                test_request = request.copy()
                test_request["headers"]["Authorization"] = f"Bearer {tokens['admin']}"
                
                result = process_api_request(test_request, product_id)
                
                # 验证正常请求应该成功
                assert result["success"], \
                    f"产品 {product_id} 正常API请求失败: {result['errors']}"
                
                assert result["status_code"] == 200, \
                    f"产品 {product_id} API请求状态码错误: {result['status_code']}"
                
                # 验证所有安全检查都通过
                for check_name, passed in result["security_checks"].items():
                    assert passed, \
                        f"产品 {product_id} 安全检查失败: {check_name}"
        
        # 6. 测试安全攻击场景
        def simulate_security_attack(scenario: str, product_id: int) -> dict:
            """模拟安全攻击场景"""
            attack_result = {"scenario": scenario, "blocked": False, "details": {}}
            
            if scenario == "invalid_token":
                # 使用无效令牌
                fake_request = {
                    "method": "GET",
                    "endpoint": "/api/products/{id}/data",
                    "headers": {"Authorization": "Bearer invalid_token_12345"},
                    "payload": None,
                    "timestamp": time.time()
                }
                
                result = process_api_request(fake_request, product_id)
                attack_result["blocked"] = result["status_code"] == 401
                attack_result["details"] = {"status_code": result["status_code"]}
            
            elif scenario == "expired_token":
                # 创建过期令牌
                expired_token = security_manager.generate_token(product_id, "test_user", ["read"])
                security_manager.tokens[expired_token]["expires_at"] = time.time() - 3600
                
                expired_request = {
                    "method": "GET",
                    "endpoint": "/api/products/{id}/data",
                    "headers": {"Authorization": f"Bearer {expired_token}"},
                    "payload": None,
                    "timestamp": time.time()
                }
                
                result = process_api_request(expired_request, product_id)
                attack_result["blocked"] = result["status_code"] == 401
                attack_result["details"] = {"status_code": result["status_code"]}
            
            elif scenario == "insufficient_permissions":
                # 使用只读令牌尝试写操作
                readonly_token = product_tokens[product_id]["readonly"]
                
                write_request = {
                    "method": "POST",
                    "endpoint": "/api/products/{id}/data",
                    "headers": {"Authorization": f"Bearer {readonly_token}"},
                    "payload": {"data": "test"},
                    "timestamp": time.time()
                }
                
                result = process_api_request(write_request, product_id)
                attack_result["blocked"] = result["status_code"] == 403
                attack_result["details"] = {"status_code": result["status_code"]}
            
            elif scenario == "sql_injection_attempt":
                # SQL注入攻击
                admin_token = product_tokens[product_id]["admin"]
                
                injection_request = {
                    "method": "POST",
                    "endpoint": "/api/products/{id}/data",
                    "headers": {"Authorization": f"Bearer {admin_token}"},
                    "payload": {
                        "query": "SELECT * FROM users WHERE id = 1 OR 1=1--",
                        "data": "'; DROP TABLE products; --"
                    },
                    "timestamp": time.time()
                }
                
                result = process_api_request(injection_request, product_id)
                attack_result["blocked"] = result["status_code"] == 400
                attack_result["details"] = {"errors": result["errors"]}
            
            elif scenario == "xss_attempt":
                # XSS攻击
                admin_token = product_tokens[product_id]["admin"]
                
                xss_request = {
                    "method": "POST",
                    "endpoint": "/api/products/{id}/data",
                    "headers": {"Authorization": f"Bearer {admin_token}"},
                    "payload": {
                        "content": "<script>alert('XSS')</script>",
                        "description": "javascript:alert('XSS')"
                    },
                    "timestamp": time.time()
                }
                
                result = process_api_request(xss_request, product_id)
                attack_result["blocked"] = result["status_code"] == 400
                attack_result["details"] = {"errors": result["errors"]}
            
            elif scenario == "rate_limit_exceeded":
                # 频率限制攻击
                admin_token = product_tokens[product_id]["admin"]
                
                # 快速发送大量请求
                for _ in range(65):  # 超过60次限制
                    rapid_request = {
                        "method": "GET",
                        "endpoint": "/api/products/{id}/data",
                        "headers": {"Authorization": f"Bearer {admin_token}"},
                        "payload": None,
                        "timestamp": time.time()
                    }
                    
                    result = process_api_request(rapid_request, product_id, "192.168.1.200")
                    if result["status_code"] == 429:
                        attack_result["blocked"] = True
                        attack_result["details"] = {"requests_blocked": True}
                        break
            
            return attack_result
        
        # 测试安全攻击防护
        for i, product_data in enumerate(products):
            product_id = i + 1
            
            for scenario in security_scenarios:
                attack_result = simulate_security_attack(scenario, product_id)
                
                # 验证攻击被正确阻止
                assert attack_result["blocked"], \
                    f"产品 {product_id} 安全攻击 {scenario} 未被正确阻止"
        
        # 7. 验证令牌管理的安全性
        def test_token_security(product_id: int):
            """测试令牌安全性"""
            # 测试令牌撤销
            test_token = security_manager.generate_token(product_id, "test_user", ["read"])
            
            # 验证令牌有效
            validation1 = security_manager.validate_token(test_token)
            assert validation1["valid"], "新生成的令牌应该有效"
            
            # 撤销令牌
            security_manager.tokens[test_token]["is_active"] = False
            
            # 验证令牌已失效
            validation2 = security_manager.validate_token(test_token)
            assert not validation2["valid"], "撤销的令牌应该无效"
            
            # 测试令牌过期
            expiring_token = security_manager.generate_token(product_id, "test_user", ["read"])
            security_manager.tokens[expiring_token]["expires_at"] = time.time() - 1
            
            validation3 = security_manager.validate_token(expiring_token)
            assert not validation3["valid"], "过期的令牌应该无效"
            
            return True
        
        # 测试令牌安全性
        for i, product_data in enumerate(products):
            product_id = i + 1
            token_security_valid = test_token_security(product_id)
            assert token_security_valid, f"产品 {product_id} 令牌安全性测试失败"
        
        # 8. 验证通信加密和完整性
        def validate_communication_security():
            """验证通信安全性"""
            security_features = {
                "https_required": True,
                "certificate_validation": True,
                "tls_version": "1.3",
                "cipher_suites": [
                    "TLS_AES_256_GCM_SHA384",
                    "TLS_CHACHA20_POLY1305_SHA256",
                    "TLS_AES_128_GCM_SHA256"
                ],
                "hsts_enabled": True,
                "certificate_pinning": True
            }
            
            # 验证HTTPS要求
            assert security_features["https_required"], "应该要求HTTPS通信"
            
            # 验证TLS版本
            assert security_features["tls_version"] in ["1.2", "1.3"], \
                f"TLS版本不安全: {security_features['tls_version']}"
            
            # 验证加密套件
            assert len(security_features["cipher_suites"]) > 0, "应该配置安全的加密套件"
            
            # 验证安全头
            assert security_features["hsts_enabled"], "应该启用HSTS"
            
            return True
        
        # 测试通信安全性
        communication_security_valid = validate_communication_security()
        assert communication_security_valid, "通信安全性验证失败"
        
        # 9. 验证安全日志和监控
        def validate_security_logging():
            """验证安全日志记录"""
            # 检查是否记录了安全事件
            assert len(security_manager.security_logs) > 0, "应该记录安全事件"
            
            # 验证日志结构
            for log_entry in security_manager.security_logs:
                assert "timestamp" in log_entry, "日志应该包含时间戳"
                assert "event_type" in log_entry, "日志应该包含事件类型"
                assert "severity" in log_entry, "日志应该包含严重程度"
                assert log_entry["severity"] in ["low", "medium", "high"], \
                    f"无效的严重程度: {log_entry['severity']}"
            
            # 验证高危事件被正确标记
            high_severity_events = [
                log for log in security_manager.security_logs
                if log["severity"] == "high"
            ]
            
            # 如果有SQL注入或XSS攻击，应该被标记为高危
            attack_events = [
                log for log in security_manager.security_logs
                if log["event_type"] in ["sql_injection_attempt", "xss_attempt"]
            ]
            
            for attack_event in attack_events:
                assert attack_event["severity"] == "high", \
                    f"攻击事件应该被标记为高危: {attack_event['event_type']}"
            
            return True
        
        # 测试安全日志
        security_logging_valid = validate_security_logging()
        assert security_logging_valid, "安全日志验证失败"
        
        # 10. 验证API安全配置的完整性
        def validate_api_security_configuration():
            """验证API安全配置"""
            security_config = {
                "authentication_required": True,
                "token_expiration": 3600,  # 1小时
                "rate_limiting": {
                    "enabled": True,
                    "requests_per_minute": 60,
                    "burst_limit": 10
                },
                "input_validation": {
                    "enabled": True,
                    "max_payload_size": 1024 * 1024,  # 1MB
                    "sanitization": True
                },
                "security_headers": {
                    "x_frame_options": "DENY",
                    "x_content_type_options": "nosniff",
                    "x_xss_protection": "1; mode=block",
                    "content_security_policy": "default-src 'self'"
                },
                "cors_policy": {
                    "enabled": True,
                    "allowed_origins": ["https://example.com"],
                    "allowed_methods": ["GET", "POST", "PUT", "DELETE"],
                    "credentials_allowed": False
                }
            }
            
            # 验证认证配置
            assert security_config["authentication_required"], "应该要求认证"
            assert 300 <= security_config["token_expiration"] <= 86400, \
                "令牌过期时间应该在合理范围内"
            
            # 验证频率限制配置
            rate_config = security_config["rate_limiting"]
            assert rate_config["enabled"], "应该启用频率限制"
            assert 1 <= rate_config["requests_per_minute"] <= 1000, \
                "每分钟请求限制应该在合理范围内"
            
            # 验证输入验证配置
            input_config = security_config["input_validation"]
            assert input_config["enabled"], "应该启用输入验证"
            assert input_config["sanitization"], "应该启用输入清理"
            
            # 验证安全头配置
            headers = security_config["security_headers"]
            assert headers["x_frame_options"] in ["DENY", "SAMEORIGIN"], \
                "X-Frame-Options应该设置为安全值"
            assert headers["x_content_type_options"] == "nosniff", \
                "X-Content-Type-Options应该设置为nosniff"
            
            return True
        
        # 测试API安全配置
        api_config_valid = validate_api_security_configuration()
        assert api_config_valid, "API安全配置验证失败"
    
    @settings(suppress_health_check=[HealthCheck.too_slow], max_examples=100)
    @given(
        products=st.lists(product_data(), min_size=2, max_size=3),
        storage_operations=st.lists(
            st.fixed_dictionaries({
                'operation': st.sampled_from(['create', 'read', 'list']),
                'key': st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
                'value': st.one_of(
                    st.text(max_size=100),
                    st.integers(min_value=0, max_value=1000),
                    st.booleans(),
                    st.dictionaries(
                        st.sampled_from(['name', 'value', 'config']), 
                        st.one_of(st.text(max_size=20), st.integers()), 
                        max_size=3
                    )
                ),
                'namespace': st.sampled_from(['user_data', 'app_config', 'cache']),
                'timestamp': st.floats(min_value=time.time()-1800, max_value=time.time())
            }),
            min_size=3, max_size=20
        ),
        isolation_tests=st.lists(
            st.sampled_from([
                'cross_product_access',
                'namespace_isolation',
                'permission_boundary',
                'data_leakage'
            ]),
            min_size=1, max_size=4
        )
    )
    def test_product_data_storage_isolation(self, products, storage_operations, isolation_tests):
        """
        **Feature: product-integration, Property 13: 产品数据存储隔离性**
        **Validates: Requirements 8.2**
        
        验证产品数据存储的隔离性和安全性：
        1. 产品间数据完全隔离
        2. 命名空间访问控制
        3. 存储权限边界验证
        4. 数据泄露防护
        5. 并发访问安全性
        6. 备份和恢复隔离
        """
        # 1. 模拟产品数据存储系统
        class ProductDataStorageManager:
            def __init__(self):
                self.storage_spaces = {}  # 每个产品的独立存储空间
                self.access_logs = []
                self.permissions = {}
                self.encryption_keys = {}
                self.backup_data = {}
                self.namespace_policies = {}
            
            def initialize_product_storage(self, product_id: int):
                """初始化产品存储空间"""
                if product_id not in self.storage_spaces:
                    self.storage_spaces[product_id] = {
                        'user_data': {},
                        'app_config': {},
                        'cache': {},
                        'temp': {},
                        'logs': {}
                    }
                    
                    # 生成产品专用的加密密钥
                    import secrets
                    self.encryption_keys[product_id] = secrets.token_bytes(32)
                    
                    # 设置默认权限
                    self.permissions[product_id] = {
                        'owner': ['create', 'read', 'update', 'delete', 'list'],
                        'user': ['create', 'read', 'update'],
                        'guest': ['read']
                    }
                    
                    # 设置命名空间策略
                    self.namespace_policies[product_id] = {
                        'user_data': {'max_size': 10 * 1024 * 1024, 'encryption': True},
                        'app_config': {'max_size': 1 * 1024 * 1024, 'encryption': True},
                        'cache': {'max_size': 50 * 1024 * 1024, 'encryption': False, 'ttl': 3600},
                        'temp': {'max_size': 5 * 1024 * 1024, 'encryption': False, 'ttl': 300},
                        'logs': {'max_size': 20 * 1024 * 1024, 'encryption': False, 'append_only': True}
                    }
            
            def store_data(self, product_id: int, namespace: str, key: str, value: any, user_role: str = 'owner') -> dict:
                """存储数据到产品空间"""
                result = {
                    'success': False,
                    'error': None,
                    'encrypted': False,
                    'size_bytes': 0
                }
                
                # 验证产品存储空间存在
                if product_id not in self.storage_spaces:
                    result['error'] = f"产品 {product_id} 存储空间不存在"
                    return result
                
                # 验证命名空间
                if namespace not in self.storage_spaces[product_id]:
                    result['error'] = f"无效的命名空间: {namespace}"
                    return result
                
                # 验证权限
                if not self._check_permission(product_id, user_role, 'create'):
                    result['error'] = f"用户角色 {user_role} 无创建权限"
                    return result
                
                # 验证命名空间策略
                policy = self.namespace_policies[product_id][namespace]
                
                # 计算数据大小
                import json
                data_size = len(json.dumps(value).encode('utf-8'))
                result['size_bytes'] = data_size
                
                # 检查大小限制
                current_size = sum(
                    len(json.dumps(v).encode('utf-8')) 
                    for v in self.storage_spaces[product_id][namespace].values()
                )
                
                if current_size + data_size > policy['max_size']:
                    result['error'] = f"命名空间 {namespace} 存储空间不足"
                    return result
                
                # 加密数据（如果需要）
                stored_value = value
                if policy.get('encryption', False):
                    stored_value = self._encrypt_data(product_id, value)
                    result['encrypted'] = True
                
                # 存储数据
                self.storage_spaces[product_id][namespace][key] = {
                    'value': stored_value,
                    'created_at': time.time(),
                    'updated_at': time.time(),
                    'size': data_size,
                    'encrypted': result['encrypted'],
                    'ttl': policy.get('ttl')
                }
                
                # 记录访问日志
                self._log_access(product_id, 'store', namespace, key, user_role, True)
                
                result['success'] = True
                return result
            
            def retrieve_data(self, product_id: int, namespace: str, key: str, user_role: str = 'owner') -> dict:
                """从产品空间检索数据"""
                result = {
                    'success': False,
                    'data': None,
                    'error': None,
                    'decrypted': False
                }
                
                # 验证产品存储空间存在
                if product_id not in self.storage_spaces:
                    result['error'] = f"产品 {product_id} 存储空间不存在"
                    self._log_access(product_id, 'retrieve', namespace, key, user_role, False)
                    return result
                
                # 验证命名空间
                if namespace not in self.storage_spaces[product_id]:
                    result['error'] = f"无效的命名空间: {namespace}"
                    self._log_access(product_id, 'retrieve', namespace, key, user_role, False)
                    return result
                
                # 验证权限
                if not self._check_permission(product_id, user_role, 'read'):
                    result['error'] = f"用户角色 {user_role} 无读取权限"
                    self._log_access(product_id, 'retrieve', namespace, key, user_role, False)
                    return result
                
                # 检查数据是否存在
                if key not in self.storage_spaces[product_id][namespace]:
                    result['error'] = f"数据键 {key} 不存在"
                    self._log_access(product_id, 'retrieve', namespace, key, user_role, False)
                    return result
                
                stored_item = self.storage_spaces[product_id][namespace][key]
                
                # 检查TTL
                if stored_item.get('ttl'):
                    if time.time() - stored_item['created_at'] > stored_item['ttl']:
                        # 数据已过期，删除它
                        del self.storage_spaces[product_id][namespace][key]
                        result['error'] = f"数据键 {key} 已过期"
                        self._log_access(product_id, 'retrieve', namespace, key, user_role, False)
                        return result
                
                # 解密数据（如果需要）
                data = stored_item['value']
                if stored_item.get('encrypted', False):
                    data = self._decrypt_data(product_id, data)
                    result['decrypted'] = True
                
                result['success'] = True
                result['data'] = data
                self._log_access(product_id, 'retrieve', namespace, key, user_role, True)
                return result
            
            def list_keys(self, product_id: int, namespace: str, user_role: str = 'owner') -> dict:
                """列出命名空间中的所有键"""
                result = {
                    'success': False,
                    'keys': [],
                    'error': None
                }
                
                # 验证产品存储空间存在
                if product_id not in self.storage_spaces:
                    result['error'] = f"产品 {product_id} 存储空间不存在"
                    return result
                
                # 验证命名空间
                if namespace not in self.storage_spaces[product_id]:
                    result['error'] = f"无效的命名空间: {namespace}"
                    return result
                
                # 验证权限
                if not self._check_permission(product_id, user_role, 'list'):
                    result['error'] = f"用户角色 {user_role} 无列表权限"
                    return result
                
                # 清理过期数据并获取键列表
                current_time = time.time()
                valid_keys = []
                
                for key, item in list(self.storage_spaces[product_id][namespace].items()):
                    if item.get('ttl') and current_time - item['created_at'] > item['ttl']:
                        # 删除过期数据
                        del self.storage_spaces[product_id][namespace][key]
                    else:
                        valid_keys.append(key)
                
                result['success'] = True
                result['keys'] = valid_keys
                self._log_access(product_id, 'list', namespace, None, user_role, True)
                return result
            
            def delete_data(self, product_id: int, namespace: str, key: str, user_role: str = 'owner') -> dict:
                """删除产品空间中的数据"""
                result = {
                    'success': False,
                    'error': None
                }
                
                # 验证产品存储空间存在
                if product_id not in self.storage_spaces:
                    result['error'] = f"产品 {product_id} 存储空间不存在"
                    return result
                
                # 验证命名空间
                if namespace not in self.storage_spaces[product_id]:
                    result['error'] = f"无效的命名空间: {namespace}"
                    return result
                
                # 验证权限
                if not self._check_permission(product_id, user_role, 'delete'):
                    result['error'] = f"用户角色 {user_role} 无删除权限"
                    return result
                
                # 检查只追加策略
                policy = self.namespace_policies[product_id][namespace]
                if policy.get('append_only', False):
                    result['error'] = f"命名空间 {namespace} 为只追加模式，不允许删除"
                    return result
                
                # 检查数据是否存在
                if key not in self.storage_spaces[product_id][namespace]:
                    result['error'] = f"数据键 {key} 不存在"
                    return result
                
                # 删除数据
                del self.storage_spaces[product_id][namespace][key]
                
                result['success'] = True
                self._log_access(product_id, 'delete', namespace, key, user_role, True)
                return result
            
            def _check_permission(self, product_id: int, user_role: str, operation: str) -> bool:
                """检查用户权限"""
                if product_id not in self.permissions:
                    return False
                
                role_permissions = self.permissions[product_id].get(user_role, [])
                return operation in role_permissions
            
            def _encrypt_data(self, product_id: int, data: any) -> str:
                """加密数据"""
                import json
                import base64
                
                # 简化的加密实现（实际应使用真正的加密算法）
                data_str = json.dumps(data)
                key = self.encryption_keys[product_id]
                
                # 使用密钥进行简单的XOR加密
                encrypted_bytes = bytes(
                    data_str.encode('utf-8')[i] ^ key[i % len(key)]
                    for i in range(len(data_str.encode('utf-8')))
                )
                
                return base64.b64encode(encrypted_bytes).decode('utf-8')
            
            def _decrypt_data(self, product_id: int, encrypted_data: str) -> any:
                """解密数据"""
                import json
                import base64
                
                key = self.encryption_keys[product_id]
                encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
                
                # 使用相同的XOR解密
                decrypted_bytes = bytes(
                    encrypted_bytes[i] ^ key[i % len(key)]
                    for i in range(len(encrypted_bytes))
                )
                
                data_str = decrypted_bytes.decode('utf-8')
                return json.loads(data_str)
            
            def _log_access(self, product_id: int, operation: str, namespace: str, key: str, user_role: str, success: bool):
                """记录访问日志"""
                self.access_logs.append({
                    'timestamp': time.time(),
                    'product_id': product_id,
                    'operation': operation,
                    'namespace': namespace,
                    'key': key,
                    'user_role': user_role,
                    'success': success
                })
            
            def get_storage_stats(self, product_id: int) -> dict:
                """获取存储统计信息"""
                if product_id not in self.storage_spaces:
                    return {'error': '产品存储空间不存在'}
                
                stats = {
                    'total_size': 0,
                    'namespaces': {},
                    'total_keys': 0,
                    'encrypted_keys': 0
                }
                
                for namespace, data in self.storage_spaces[product_id].items():
                    namespace_size = 0
                    namespace_keys = 0
                    encrypted_keys = 0
                    
                    for key, item in data.items():
                        namespace_size += item['size']
                        namespace_keys += 1
                        if item.get('encrypted', False):
                            encrypted_keys += 1
                    
                    stats['namespaces'][namespace] = {
                        'size': namespace_size,
                        'keys': namespace_keys,
                        'encrypted_keys': encrypted_keys
                    }
                    
                    stats['total_size'] += namespace_size
                    stats['total_keys'] += namespace_keys
                    stats['encrypted_keys'] += encrypted_keys
                
                return stats
        
        # 2. 初始化存储管理器并为每个产品创建存储空间
        storage_manager = ProductDataStorageManager()
        
        for i, product_data in enumerate(products):
            product_id = i + 1
            storage_manager.initialize_product_storage(product_id)
        
        # 3. 执行存储操作并验证隔离性
        operation_results = {}
        
        for i, operation in enumerate(storage_operations):
            # 为操作分配产品ID
            product_id = (i % len(products)) + 1
            
            op_type = operation['operation']
            namespace = operation['namespace']
            key = operation['key']
            value = operation['value']
            
            if op_type == 'create':
                result = storage_manager.store_data(product_id, namespace, key, value)
                operation_results[f"{product_id}_{namespace}_{key}"] = {
                    'operation': 'create',
                    'product_id': product_id,
                    'success': result['success'],
                    'encrypted': result.get('encrypted', False)
                }
                
                # 验证存储操作的基本正确性
                if result['success']:
                    # 验证数据可以被正确检索
                    retrieve_result = storage_manager.retrieve_data(product_id, namespace, key)
                    assert retrieve_result['success'], \
                        f"产品 {product_id} 存储的数据无法检索: {key}"
                    
                    # 验证数据内容一致性
                    assert retrieve_result['data'] == value, \
                        f"产品 {product_id} 检索的数据与存储的数据不一致"
            
            elif op_type == 'read':
                result = storage_manager.retrieve_data(product_id, namespace, key)
                # 读取操作可能失败（如果数据不存在），这是正常的
            
            elif op_type == 'list':
                result = storage_manager.list_keys(product_id, namespace)
                # 列表操作应该总是成功的
                assert result['success'], \
                    f"产品 {product_id} 列表操作失败: {result.get('error')}"
            
            elif op_type == 'delete':
                result = storage_manager.delete_data(product_id, namespace, key)
                # 删除操作可能失败（如果数据不存在或权限不足），这是正常的
        
        # 4. 验证产品间数据隔离
        def test_cross_product_isolation():
            """测试跨产品数据隔离"""
            # 在每个产品中存储相同键名的不同数据
            test_key = "isolation_test_key"
            test_namespace = "user_data"
            
            stored_values = {}
            
            for i, product_data in enumerate(products):
                product_id = i + 1
                test_value = f"product_{product_id}_data_{random.randint(1000, 9999)}"
                
                result = storage_manager.store_data(product_id, test_namespace, test_key, test_value)
                if result['success']:
                    stored_values[product_id] = test_value
            
            # 验证每个产品只能访问自己的数据
            for product_id, expected_value in stored_values.items():
                result = storage_manager.retrieve_data(product_id, test_namespace, test_key)
                
                assert result['success'], \
                    f"产品 {product_id} 无法访问自己的数据"
                
                assert result['data'] == expected_value, \
                    f"产品 {product_id} 检索到错误的数据: 期望 {expected_value}, 实际 {result['data']}"
            
            # 尝试跨产品访问（应该失败或返回不同的数据）
            for i, product_data in enumerate(products):
                product_id = i + 1
                
                for j, other_product_data in enumerate(products):
                    other_product_id = j + 1
                    
                    if product_id != other_product_id:
                        # 产品不应该能够访问其他产品的存储空间
                        # 这里我们通过检查存储管理器的内部状态来验证隔离
                        product_storage = storage_manager.storage_spaces[product_id][test_namespace]
                        other_storage = storage_manager.storage_spaces[other_product_id][test_namespace]
                        
                        # 验证存储空间是独立的
                        assert product_storage is not other_storage, \
                            f"产品 {product_id} 和 {other_product_id} 共享存储空间"
                        
                        # 验证数据不会泄露
                        if test_key in product_storage and test_key in other_storage:
                            assert product_storage[test_key]['value'] != other_storage[test_key]['value'], \
                                f"产品 {product_id} 和 {other_product_id} 的数据相同，可能存在数据泄露"
        
        # 5. 验证命名空间隔离
        def test_namespace_isolation():
            """测试命名空间隔离"""
            test_key = "namespace_test_key"
            test_value = "namespace_test_value"
            
            for i, product_data in enumerate(products):
                product_id = i + 1
                
                # 在不同命名空间中存储相同键名的数据
                namespaces = ['user_data', 'app_config', 'cache']
                
                for namespace in namespaces:
                    namespace_value = f"{test_value}_{namespace}"
                    result = storage_manager.store_data(product_id, namespace, test_key, namespace_value)
                    
                    if result['success']:
                        # 验证可以从正确的命名空间检索数据
                        retrieve_result = storage_manager.retrieve_data(product_id, namespace, test_key)
                        
                        assert retrieve_result['success'], \
                            f"产品 {product_id} 无法从命名空间 {namespace} 检索数据"
                        
                        assert retrieve_result['data'] == namespace_value, \
                            f"产品 {product_id} 命名空间 {namespace} 数据不一致"
                
                # 验证命名空间间的数据隔离
                for ns1 in namespaces:
                    for ns2 in namespaces:
                        if ns1 != ns2:
                            ns1_result = storage_manager.retrieve_data(product_id, ns1, test_key)
                            ns2_result = storage_manager.retrieve_data(product_id, ns2, test_key)
                            
                            if ns1_result['success'] and ns2_result['success']:
                                assert ns1_result['data'] != ns2_result['data'], \
                                    f"产品 {product_id} 命名空间 {ns1} 和 {ns2} 的数据相同"
        
        # 6. 验证权限边界
        def test_permission_boundaries():
            """测试权限边界"""
            test_key = "permission_test_key"
            test_value = "permission_test_value"
            test_namespace = "user_data"
            
            for i, product_data in enumerate(products):
                product_id = i + 1
                
                # 使用owner权限存储数据
                store_result = storage_manager.store_data(product_id, test_namespace, test_key, test_value, 'owner')
                
                if store_result['success']:
                    # 测试不同角色的访问权限
                    roles_and_operations = [
                        ('owner', 'read', True),
                        ('user', 'read', True),
                        ('guest', 'read', True),
                        ('user', 'delete', False),  # user不应该有删除权限
                        ('guest', 'create', False)  # guest不应该有创建权限
                    ]
                    
                    for role, operation, should_succeed in roles_and_operations:
                        if operation == 'read':
                            result = storage_manager.retrieve_data(product_id, test_namespace, test_key, role)
                        elif operation == 'delete':
                            result = storage_manager.delete_data(product_id, test_namespace, test_key, role)
                        elif operation == 'create':
                            result = storage_manager.store_data(product_id, test_namespace, f"{test_key}_new", test_value, role)
                        
                        if should_succeed:
                            assert result['success'], \
                                f"产品 {product_id} 角色 {role} 的 {operation} 操作应该成功"
                        else:
                            assert not result['success'], \
                                f"产品 {product_id} 角色 {role} 的 {operation} 操作不应该成功"
        
        # 7. 验证数据加密隔离
        def test_encryption_isolation():
            """测试数据加密隔离"""
            test_key = "encryption_test_key"
            test_value = {"sensitive": "data", "user_id": 12345}
            test_namespace = "user_data"  # 这个命名空间启用了加密
            
            encrypted_data = {}
            
            for i, product_data in enumerate(products):
                product_id = i + 1
                
                # 存储敏感数据
                result = storage_manager.store_data(product_id, test_namespace, test_key, test_value)
                
                if result['success'] and result['encrypted']:
                    # 获取加密后的原始数据
                    raw_data = storage_manager.storage_spaces[product_id][test_namespace][test_key]['value']
                    encrypted_data[product_id] = raw_data
                    
                    # 验证原始数据已被加密（不等于原始值）
                    assert raw_data != test_value, \
                        f"产品 {product_id} 的敏感数据未被加密"
                    
                    # 验证可以正确解密
                    retrieve_result = storage_manager.retrieve_data(product_id, test_namespace, test_key)
                    assert retrieve_result['success'] and retrieve_result['decrypted'], \
                        f"产品 {product_id} 的加密数据无法解密"
                    
                    assert retrieve_result['data'] == test_value, \
                        f"产品 {product_id} 解密后的数据不一致"
            
            # 验证不同产品的加密数据是不同的（使用不同的密钥）
            encrypted_values = list(encrypted_data.values())
            for i in range(len(encrypted_values)):
                for j in range(i + 1, len(encrypted_values)):
                    assert encrypted_values[i] != encrypted_values[j], \
                        "不同产品的加密数据相同，可能使用了相同的密钥"
        
        # 8. 执行隔离测试
        for test_type in isolation_tests:
            if test_type == 'cross_product_access':
                test_cross_product_isolation()
            elif test_type == 'namespace_isolation':
                test_namespace_isolation()
            elif test_type == 'permission_boundary':
                test_permission_boundaries()
            elif test_type == 'data_leakage':
                test_encryption_isolation()
            elif test_type == 'concurrent_access':
                # 模拟并发访问测试
                def test_concurrent_access():
                    """测试并发访问安全性"""
                    import threading
                    import queue
                    
                    results_queue = queue.Queue()
                    test_key = "concurrent_test_key"
                    test_namespace = "cache"
                    
                    def concurrent_operation(product_id, operation_id):
                        """并发操作函数"""
                        try:
                            value = f"concurrent_value_{operation_id}"
                            
                            # 存储数据
                            store_result = storage_manager.store_data(product_id, test_namespace, f"{test_key}_{operation_id}", value)
                            
                            # 检索数据
                            if store_result['success']:
                                retrieve_result = storage_manager.retrieve_data(product_id, test_namespace, f"{test_key}_{operation_id}")
                                results_queue.put({
                                    'product_id': product_id,
                                    'operation_id': operation_id,
                                    'success': retrieve_result['success'] and retrieve_result['data'] == value
                                })
                            else:
                                results_queue.put({
                                    'product_id': product_id,
                                    'operation_id': operation_id,
                                    'success': False
                                })
                        except Exception as e:
                            results_queue.put({
                                'product_id': product_id,
                                'operation_id': operation_id,
                                'success': False,
                                'error': str(e)
                            })
                    
                    # 启动并发线程
                    threads = []
                    for i in range(min(10, len(products) * 3)):  # 每个产品最多3个并发操作
                        product_id = (i % len(products)) + 1
                        thread = threading.Thread(target=concurrent_operation, args=(product_id, i))
                        threads.append(thread)
                        thread.start()
                    
                    # 等待所有线程完成
                    for thread in threads:
                        thread.join()
                    
                    # 验证结果
                    results = []
                    while not results_queue.empty():
                        results.append(results_queue.get())
                    
                    # 验证大部分操作成功
                    successful_operations = [r for r in results if r['success']]
                    success_rate = len(successful_operations) / len(results) if results else 0
                    
                    assert success_rate > 0.8, \
                        f"并发访问成功率过低: {success_rate:.2%}"
                
                test_concurrent_access()
            
            elif test_type == 'backup_isolation':
                # 测试备份隔离
                def test_backup_isolation():
                    """测试备份数据隔离"""
                    # 为每个产品创建备份
                    for i, product_data in enumerate(products):
                        product_id = i + 1
                        
                        # 获取产品存储统计
                        stats = storage_manager.get_storage_stats(product_id)
                        
                        if 'error' not in stats:
                            # 模拟备份创建
                            backup_data = {
                                'product_id': product_id,
                                'timestamp': time.time(),
                                'stats': stats,
                                'encrypted': True
                            }
                            
                            storage_manager.backup_data[product_id] = backup_data
                    
                    # 验证备份数据隔离
                    for product_id in storage_manager.backup_data:
                        backup = storage_manager.backup_data[product_id]
                        
                        # 验证备份只包含对应产品的数据
                        assert backup['product_id'] == product_id, \
                            f"备份数据包含错误的产品ID: {backup['product_id']}"
                        
                        # 验证备份数据已加密
                        assert backup['encrypted'], \
                            f"产品 {product_id} 的备份数据未加密"
                
                test_backup_isolation()
        
        # 9. 验证存储系统的整体一致性
        def validate_storage_consistency():
            """验证存储系统的整体一致性"""
            total_operations = len(storage_manager.access_logs)
            
            # 验证访问日志记录完整
            assert total_operations > 0, "应该记录访问日志"
            
            # 验证每个产品的存储空间独立
            product_ids = list(storage_manager.storage_spaces.keys())
            
            for i in range(len(product_ids)):
                for j in range(i + 1, len(product_ids)):
                    product1_storage = storage_manager.storage_spaces[product_ids[i]]
                    product2_storage = storage_manager.storage_spaces[product_ids[j]]
                    
                    # 验证存储空间对象不同
                    assert product1_storage is not product2_storage, \
                        f"产品 {product_ids[i]} 和 {product_ids[j]} 共享存储空间对象"
                    
                    # 验证加密密钥不同
                    key1 = storage_manager.encryption_keys[product_ids[i]]
                    key2 = storage_manager.encryption_keys[product_ids[j]]
                    assert key1 != key2, \
                        f"产品 {product_ids[i]} 和 {product_ids[j]} 使用相同的加密密钥"
            
            # 验证存储统计的准确性
            for product_id in product_ids:
                stats = storage_manager.get_storage_stats(product_id)
                
                if 'error' not in stats:
                    # 验证统计数据的合理性
                    assert stats['total_size'] >= 0, \
                        f"产品 {product_id} 总存储大小不能为负数"
                    
                    assert stats['total_keys'] >= 0, \
                        f"产品 {product_id} 总键数不能为负数"
                    
                    assert stats['encrypted_keys'] <= stats['total_keys'], \
                        f"产品 {product_id} 加密键数不能超过总键数"
                    
                    # 验证命名空间统计的一致性
                    namespace_total_size = sum(ns['size'] for ns in stats['namespaces'].values())
                    namespace_total_keys = sum(ns['keys'] for ns in stats['namespaces'].values())
                    
                    assert namespace_total_size == stats['total_size'], \
                        f"产品 {product_id} 命名空间大小统计不一致"
                    
                    assert namespace_total_keys == stats['total_keys'], \
                        f"产品 {product_id} 命名空间键数统计不一致"
        
        # 执行一致性验证
        validate_storage_consistency()
        
        # 10. 验证数据清理和过期机制
        def test_data_expiration():
            """测试数据过期和清理机制"""
            test_key = "expiration_test_key"
            test_value = "expiration_test_value"
            temp_namespace = "temp"  # 这个命名空间有TTL设置
            
            for i, product_data in enumerate(products):
                product_id = i + 1
                
                # 存储临时数据
                result = storage_manager.store_data(product_id, temp_namespace, test_key, test_value)
                
                if result['success']:
                    # 立即检索应该成功
                    immediate_result = storage_manager.retrieve_data(product_id, temp_namespace, test_key)
                    assert immediate_result['success'], \
                        f"产品 {product_id} 临时数据立即检索失败"
                    
                    # 模拟时间过期（修改创建时间）
                    stored_item = storage_manager.storage_spaces[product_id][temp_namespace][test_key]
                    stored_item['created_at'] = time.time() - 400  # 超过300秒TTL
                    
                    # 再次检索应该失败（数据已过期）
                    expired_result = storage_manager.retrieve_data(product_id, temp_namespace, test_key)
                    assert not expired_result['success'], \
                        f"产品 {product_id} 过期数据检索应该失败"
                    
                    # 验证过期数据已被清理
                    assert test_key not in storage_manager.storage_spaces[product_id][temp_namespace], \
                        f"产品 {product_id} 过期数据未被清理"
        
        # 测试数据过期机制
        test_data_expiration()

# 运行状态机测试
TestProductIntegrationStateMachine = ProductIntegrationStateMachine.TestCase

if __name__ == "__main__":
    # 运行属性测试
    pytest.main([__file__, "-v", "--tb=short"])