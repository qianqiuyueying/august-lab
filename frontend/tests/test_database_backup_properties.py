"""
数据库备份往返一致性属性测试

**Feature: personal-website, Property 17: 数据库备份往返一致性**
**Validates: Requirements 9.4**

这些测试验证数据库备份和恢复操作的一致性，确保备份后的数据能够完整恢复。
"""

import pytest
from hypothesis import given, strategies as st, assume, settings
from typing import Dict, List, Any, Optional
import json
import sqlite3
import tempfile
import os
from datetime import datetime, timezone
import hashlib


# 数据生成策略
@st.composite
def portfolio_data(draw):
    """生成作品数据"""
    return {
        'id': draw(st.integers(min_value=1, max_value=10000)),
        'title': draw(st.text(min_size=1, max_size=100)),
        'description': draw(st.one_of(st.none(), st.text(max_size=500))),
        'tech_stack': draw(st.lists(st.text(min_size=1, max_size=50), min_size=0, max_size=10)),
        'project_url': draw(st.one_of(st.none(), st.text(min_size=1, max_size=200))),
        'github_url': draw(st.one_of(st.none(), st.text(min_size=1, max_size=200))),
        'image_url': draw(st.one_of(st.none(), st.text(min_size=1, max_size=200))),
        'display_order': draw(st.integers(min_value=0, max_value=1000)),
        'is_featured': draw(st.booleans()),
        'created_at': draw(st.datetimes(min_value=datetime(2020, 1, 1))).isoformat(),
        'updated_at': draw(st.datetimes(min_value=datetime(2020, 1, 1))).isoformat()
    }


@st.composite
def blog_data(draw):
    """生成博客数据"""
    return {
        'id': draw(st.integers(min_value=1, max_value=10000)),
        'title': draw(st.text(min_size=1, max_size=200)),
        'content': draw(st.text(min_size=1, max_size=5000)),
        'summary': draw(st.one_of(st.none(), st.text(max_size=300))),
        'tags': draw(st.lists(st.text(min_size=1, max_size=30), min_size=0, max_size=10)),
        'is_published': draw(st.booleans()),
        'cover_image': draw(st.one_of(st.none(), st.text(min_size=1, max_size=200))),
        'created_at': draw(st.datetimes(min_value=datetime(2020, 1, 1))).isoformat(),
        'updated_at': draw(st.datetimes(min_value=datetime(2020, 1, 1))).isoformat()
    }


@st.composite
def profile_data(draw):
    """生成个人信息数据"""
    skills = draw(st.lists(
        st.fixed_dictionaries({
            'name': st.text(min_size=1, max_size=50),
            'category': st.text(min_size=1, max_size=30),
            'level': st.integers(min_value=1, max_value=100)
        }),
        min_size=0,
        max_size=20
    ))
    
    return {
        'id': 1,  # 个人信息通常只有一条记录
        'name': draw(st.text(min_size=1, max_size=100)),
        'title': draw(st.text(min_size=1, max_size=100)),
        'bio': draw(st.text(min_size=1, max_size=1000)),
        'avatar_url': draw(st.one_of(st.none(), st.text(min_size=1, max_size=200))),
        'github_url': draw(st.one_of(st.none(), st.text(min_size=1, max_size=200))),
        'linkedin_url': draw(st.one_of(st.none(), st.text(min_size=1, max_size=200))),
        'twitter_url': draw(st.one_of(st.none(), st.text(min_size=1, max_size=200))),
        'skills': skills,
        'created_at': draw(st.datetimes(min_value=datetime(2020, 1, 1))).isoformat(),
        'updated_at': draw(st.datetimes(min_value=datetime(2020, 1, 1))).isoformat()
    }


@st.composite
def database_content(draw):
    """生成完整的数据库内容"""
    portfolios = draw(st.lists(portfolio_data(), min_size=0, max_size=20))
    blogs = draw(st.lists(blog_data(), min_size=0, max_size=20))
    profile = draw(st.one_of(st.none(), profile_data()))
    
    # 确保ID唯一性
    portfolio_ids = set()
    unique_portfolios = []
    for portfolio in portfolios:
        if portfolio['id'] not in portfolio_ids:
            portfolio_ids.add(portfolio['id'])
            unique_portfolios.append(portfolio)
    
    blog_ids = set()
    unique_blogs = []
    for blog in blogs:
        if blog['id'] not in blog_ids:
            blog_ids.add(blog['id'])
            unique_blogs.append(blog)
    
    return {
        'portfolios': unique_portfolios,
        'blogs': unique_blogs,
        'profile': profile
    }


class DatabaseBackupManager:
    """数据库备份管理器"""
    
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
    
    def create_database(self, content: Dict[str, Any]) -> str:
        """创建数据库并填充数据"""
        db_path = os.path.join(self.temp_dir, f"test_{datetime.now().timestamp()}.db")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 创建表结构
        cursor.execute('''
            CREATE TABLE portfolios (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                tech_stack TEXT,
                project_url TEXT,
                github_url TEXT,
                image_url TEXT,
                display_order INTEGER DEFAULT 0,
                is_featured BOOLEAN DEFAULT FALSE,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE blogs (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                summary TEXT,
                tags TEXT,
                is_published BOOLEAN DEFAULT FALSE,
                cover_image TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE profiles (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                title TEXT NOT NULL,
                bio TEXT NOT NULL,
                avatar_url TEXT,
                github_url TEXT,
                linkedin_url TEXT,
                twitter_url TEXT,
                skills TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')
        
        # 插入数据
        for portfolio in content['portfolios']:
            cursor.execute('''
                INSERT INTO portfolios 
                (id, title, description, tech_stack, project_url, github_url, 
                 image_url, display_order, is_featured, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                portfolio['id'], portfolio['title'], portfolio['description'],
                json.dumps(portfolio['tech_stack']), portfolio['project_url'],
                portfolio['github_url'], portfolio['image_url'],
                portfolio['display_order'], portfolio['is_featured'],
                portfolio['created_at'], portfolio['updated_at']
            ))
        
        for blog in content['blogs']:
            cursor.execute('''
                INSERT INTO blogs 
                (id, title, content, summary, tags, is_published, 
                 cover_image, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                blog['id'], blog['title'], blog['content'], blog['summary'],
                json.dumps(blog['tags']), blog['is_published'],
                blog['cover_image'], blog['created_at'], blog['updated_at']
            ))
        
        if content['profile']:
            profile = content['profile']
            cursor.execute('''
                INSERT INTO profiles 
                (id, name, title, bio, avatar_url, github_url, linkedin_url,
                 twitter_url, skills, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                profile['id'], profile['name'], profile['title'], profile['bio'],
                profile['avatar_url'], profile['github_url'], profile['linkedin_url'],
                profile['twitter_url'], json.dumps(profile['skills']),
                profile['created_at'], profile['updated_at']
            ))
        
        conn.commit()
        conn.close()
        
        return db_path
    
    def backup_database(self, db_path: str) -> str:
        """备份数据库"""
        backup_path = db_path + '.backup'
        
        # 使用SQLite的备份API
        source = sqlite3.connect(db_path)
        backup = sqlite3.connect(backup_path)
        
        source.backup(backup)
        
        source.close()
        backup.close()
        
        return backup_path
    
    def restore_database(self, backup_path: str) -> str:
        """从备份恢复数据库"""
        restore_path = backup_path.replace('.backup', '.restored')
        
        # 复制备份文件
        backup = sqlite3.connect(backup_path)
        restored = sqlite3.connect(restore_path)
        
        backup.backup(restored)
        
        backup.close()
        restored.close()
        
        return restore_path
    
    def read_database_content(self, db_path: str) -> Dict[str, Any]:
        """读取数据库内容"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 读取作品
        cursor.execute('SELECT * FROM portfolios ORDER BY id')
        portfolio_rows = cursor.fetchall()
        portfolios = []
        for row in portfolio_rows:
            portfolios.append({
                'id': row[0],
                'title': row[1],
                'description': row[2],
                'tech_stack': json.loads(row[3]) if row[3] else [],
                'project_url': row[4],
                'github_url': row[5],
                'image_url': row[6],
                'display_order': row[7],
                'is_featured': bool(row[8]),
                'created_at': row[9],
                'updated_at': row[10]
            })
        
        # 读取博客
        cursor.execute('SELECT * FROM blogs ORDER BY id')
        blog_rows = cursor.fetchall()
        blogs = []
        for row in blog_rows:
            blogs.append({
                'id': row[0],
                'title': row[1],
                'content': row[2],
                'summary': row[3],
                'tags': json.loads(row[4]) if row[4] else [],
                'is_published': bool(row[5]),
                'cover_image': row[6],
                'created_at': row[7],
                'updated_at': row[8]
            })
        
        # 读取个人信息
        cursor.execute('SELECT * FROM profiles LIMIT 1')
        profile_row = cursor.fetchone()
        profile = None
        if profile_row:
            profile = {
                'id': profile_row[0],
                'name': profile_row[1],
                'title': profile_row[2],
                'bio': profile_row[3],
                'avatar_url': profile_row[4],
                'github_url': profile_row[5],
                'linkedin_url': profile_row[6],
                'twitter_url': profile_row[7],
                'skills': json.loads(profile_row[8]) if profile_row[8] else [],
                'created_at': profile_row[9],
                'updated_at': profile_row[10]
            }
        
        conn.close()
        
        return {
            'portfolios': portfolios,
            'blogs': blogs,
            'profile': profile
        }
    
    def calculate_content_hash(self, content: Dict[str, Any]) -> str:
        """计算内容哈希值"""
        content_str = json.dumps(content, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(content_str.encode()).hexdigest()
    
    def cleanup(self):
        """清理临时文件"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)


# 属性测试
class TestDatabaseBackupProperties:
    """数据库备份往返一致性属性测试"""
    
    @given(content=database_content())
    @settings(max_examples=50, deadline=30000)
    def test_backup_restore_round_trip_consistency(self, content):
        """
        **Feature: personal-website, Property 17: 数据库备份往返一致性**
        **Validates: Requirements 9.4**
        
        测试数据库备份和恢复的往返一致性
        对于任何数据库内容，备份后恢复应该得到相同的数据
        """
        manager = DatabaseBackupManager()
        
        try:
            # 创建原始数据库
            original_db = manager.create_database(content)
            
            # 备份数据库
            backup_path = manager.backup_database(original_db)
            
            # 从备份恢复
            restored_db = manager.restore_database(backup_path)
            
            # 读取原始和恢复的内容
            original_content = manager.read_database_content(original_db)
            restored_content = manager.read_database_content(restored_db)
            
            # 验证内容一致性
            assert original_content == restored_content, \
                f"备份恢复后内容不一致:\n原始: {original_content}\n恢复: {restored_content}"
            
            # 验证哈希一致性
            original_hash = manager.calculate_content_hash(original_content)
            restored_hash = manager.calculate_content_hash(restored_content)
            
            assert original_hash == restored_hash, \
                f"备份恢复后哈希不一致: {original_hash} != {restored_hash}"
        
        finally:
            manager.cleanup()
    
    @given(content=database_content())
    @settings(max_examples=30, deadline=30000)
    def test_multiple_backup_restore_cycles(self, content):
        """
        **Feature: personal-website, Property 17: 数据库备份往返一致性**
        **Validates: Requirements 9.4**
        
        测试多次备份恢复循环的一致性
        多次备份恢复操作不应该改变数据
        """
        assume(len(content['portfolios']) > 0 or len(content['blogs']) > 0 or content['profile'] is not None)
        
        manager = DatabaseBackupManager()
        
        try:
            # 创建原始数据库
            current_db = manager.create_database(content)
            original_content = manager.read_database_content(current_db)
            
            # 执行多次备份恢复循环
            for cycle in range(3):
                # 备份
                backup_path = manager.backup_database(current_db)
                
                # 恢复
                restored_db = manager.restore_database(backup_path)
                
                # 验证内容
                restored_content = manager.read_database_content(restored_db)
                
                assert restored_content == original_content, \
                    f"第{cycle+1}次循环后内容不一致"
                
                # 使用恢复的数据库进行下一次循环
                current_db = restored_db
        
        finally:
            manager.cleanup()
    
    @given(content=database_content())
    @settings(max_examples=30, deadline=30000)
    def test_backup_file_integrity(self, content):
        """
        **Feature: personal-website, Property 17: 数据库备份往返一致性**
        **Validates: Requirements 9.4**
        
        测试备份文件的完整性
        备份文件应该是有效的SQLite数据库
        """
        manager = DatabaseBackupManager()
        
        try:
            # 创建原始数据库
            original_db = manager.create_database(content)
            
            # 备份数据库
            backup_path = manager.backup_database(original_db)
            
            # 验证备份文件存在且可读
            assert os.path.exists(backup_path), "备份文件不存在"
            assert os.path.getsize(backup_path) > 0, "备份文件为空"
            
            # 验证备份文件是有效的SQLite数据库
            conn = sqlite3.connect(backup_path)
            cursor = conn.cursor()
            
            # 检查表结构
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            expected_tables = {'portfolios', 'blogs', 'profiles'}
            actual_tables = set(tables)
            
            assert expected_tables.issubset(actual_tables), \
                f"备份文件缺少必要的表: {expected_tables - actual_tables}"
            
            conn.close()
        
        finally:
            manager.cleanup()
    
    @given(content=database_content())
    @settings(max_examples=30, deadline=30000)
    def test_backup_data_completeness(self, content):
        """
        **Feature: personal-website, Property 17: 数据库备份往返一致性**
        **Validates: Requirements 9.4**
        
        测试备份数据的完整性
        备份应该包含所有原始数据
        """
        manager = DatabaseBackupManager()
        
        try:
            # 创建原始数据库
            original_db = manager.create_database(content)
            
            # 备份数据库
            backup_path = manager.backup_database(original_db)
            
            # 读取原始和备份的内容
            original_content = manager.read_database_content(original_db)
            backup_content = manager.read_database_content(backup_path)
            
            # 验证记录数量
            assert len(backup_content['portfolios']) == len(original_content['portfolios']), \
                "备份中作品数量不匹配"
            
            assert len(backup_content['blogs']) == len(original_content['blogs']), \
                "备份中博客数量不匹配"
            
            assert (backup_content['profile'] is None) == (original_content['profile'] is None), \
                "备份中个人信息状态不匹配"
            
            # 验证具体内容
            for i, portfolio in enumerate(original_content['portfolios']):
                backup_portfolio = backup_content['portfolios'][i]
                assert portfolio == backup_portfolio, \
                    f"第{i}个作品备份不匹配: {portfolio} != {backup_portfolio}"
            
            for i, blog in enumerate(original_content['blogs']):
                backup_blog = backup_content['blogs'][i]
                assert blog == backup_blog, \
                    f"第{i}个博客备份不匹配: {blog} != {backup_blog}"
            
            if original_content['profile']:
                assert backup_content['profile'] == original_content['profile'], \
                    "个人信息备份不匹配"
        
        finally:
            manager.cleanup()
    
    @given(content=database_content())
    @settings(max_examples=20, deadline=30000)
    def test_backup_metadata_preservation(self, content):
        """
        **Feature: personal-website, Property 17: 数据库备份往返一致性**
        **Validates: Requirements 9.4**
        
        测试备份元数据的保持
        备份应该保持所有元数据信息
        """
        assume(len(content['portfolios']) > 0 or len(content['blogs']) > 0)
        
        manager = DatabaseBackupManager()
        
        try:
            # 创建原始数据库
            original_db = manager.create_database(content)
            
            # 备份数据库
            backup_path = manager.backup_database(original_db)
            
            # 恢复数据库
            restored_db = manager.restore_database(backup_path)
            
            # 验证数据库结构
            original_conn = sqlite3.connect(original_db)
            restored_conn = sqlite3.connect(restored_db)
            
            # 检查表结构
            original_cursor = original_conn.cursor()
            restored_cursor = restored_conn.cursor()
            
            for table in ['portfolios', 'blogs', 'profiles']:
                original_cursor.execute(f"PRAGMA table_info({table})")
                original_schema = original_cursor.fetchall()
                
                restored_cursor.execute(f"PRAGMA table_info({table})")
                restored_schema = restored_cursor.fetchall()
                
                assert original_schema == restored_schema, \
                    f"表 {table} 的结构在备份恢复后发生变化"
            
            original_conn.close()
            restored_conn.close()
        
        finally:
            manager.cleanup()


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--tb=short"])