"""
数据库迁移工具
用于处理数据库结构变更和数据迁移
"""

from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from .database import SQLALCHEMY_DATABASE_URL, Base
from .models import Portfolio, Blog, Profile, Session
import json
from datetime import datetime

class DatabaseMigration:
    def __init__(self):
        self.engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def get_table_info(self, table_name):
        """获取表信息"""
        inspector = inspect(self.engine)
        if inspector.has_table(table_name):
            columns = inspector.get_columns(table_name)
            indexes = inspector.get_indexes(table_name)
            return {"columns": columns, "indexes": indexes}
        return None
    
    def table_exists(self, table_name):
        """检查表是否存在"""
        inspector = inspect(self.engine)
        return inspector.has_table(table_name)
    
    def column_exists(self, table_name, column_name):
        """检查列是否存在"""
        table_info = self.get_table_info(table_name)
        if table_info:
            return any(col['name'] == column_name for col in table_info['columns'])
        return False
    
    def add_column_if_not_exists(self, table_name, column_definition):
        """如果列不存在则添加"""
        column_name = column_definition.split()[0]
        if not self.column_exists(table_name, column_name):
            with self.engine.connect() as conn:
                conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_definition}"))
                conn.commit()
            print(f"已添加列 {column_name} 到表 {table_name}")
        else:
            print(f"列 {column_name} 已存在于表 {table_name}")
    
    def create_index_if_not_exists(self, index_name, table_name, columns):
        """如果索引不存在则创建"""
        inspector = inspect(self.engine)
        if self.table_exists(table_name):
            indexes = inspector.get_indexes(table_name)
            if not any(idx['name'] == index_name for idx in indexes):
                columns_str = ', '.join(columns)
                with self.engine.connect() as conn:
                    conn.execute(text(f"CREATE INDEX {index_name} ON {table_name} ({columns_str})"))
                    conn.commit()
                print(f"已创建索引 {index_name}")
            else:
                print(f"索引 {index_name} 已存在")
    
    def migrate_to_v1_1(self):
        """迁移到版本 1.1：添加索引优化"""
        print("开始迁移到版本 1.1...")
        
        # 为 Portfolio 表添加索引
        if self.table_exists("portfolio"):
            self.create_index_if_not_exists(
                "idx_portfolio_order_created", 
                "portfolio", 
                ["display_order", "created_at"]
            )
            self.create_index_if_not_exists(
                "idx_portfolio_featured_created", 
                "portfolio", 
                ["is_featured", "created_at"]
            )
        
        # 为 Blog 表添加索引
        if self.table_exists("blog"):
            self.create_index_if_not_exists(
                "idx_blog_published_date", 
                "blog", 
                ["is_published", "published_at"]
            )
            self.create_index_if_not_exists(
                "idx_blog_published_created", 
                "blog", 
                ["is_published", "created_at"]
            )
        
        # 为 Session 表添加索引
        if self.table_exists("sessions"):
            self.create_index_if_not_exists(
                "idx_session_active_expires", 
                "sessions", 
                ["is_active", "expires_at"]
            )
            self.create_index_if_not_exists(
                "idx_session_user_active", 
                "sessions", 
                ["user_id", "is_active"]
            )
        
        print("版本 1.1 迁移完成")
    
    def migrate_json_fields(self):
        """迁移 JSON 字段：确保空值被正确处理"""
        print("开始迁移 JSON 字段...")
        
        db = self.SessionLocal()
        try:
            # 修复 Portfolio 表的 tech_stack 字段
            portfolios = db.query(Portfolio).filter(Portfolio.tech_stack.is_(None)).all()
            for portfolio in portfolios:
                portfolio.tech_stack = []
            
            # 修复 Blog 表的 tags 字段
            blogs = db.query(Blog).filter(Blog.tags.is_(None)).all()
            for blog in blogs:
                blog.tags = []
            
            # 修复 Profile 表的 skills 字段
            profiles = db.query(Profile).filter(Profile.skills.is_(None)).all()
            for profile in profiles:
                profile.skills = []
            
            db.commit()
            print("JSON 字段迁移完成")
        except Exception as e:
            print(f"JSON 字段迁移失败: {e}")
            db.rollback()
        finally:
            db.close()
    
    def run_all_migrations(self):
        """运行所有迁移"""
        print("开始运行所有数据库迁移...")
        
        try:
            self.migrate_to_v1_1()
            self.migrate_json_fields()
            print("所有迁移完成")
        except Exception as e:
            print(f"迁移过程中出错: {e}")
            raise
    
    def check_database_health(self):
        """检查数据库健康状态"""
        print("检查数据库健康状态...")
        
        issues = []
        
        # 检查必要的表是否存在
        required_tables = ["portfolio", "blog", "profile", "sessions"]
        for table in required_tables:
            if not self.table_exists(table):
                issues.append(f"缺少必要的表: {table}")
        
        # 检查数据完整性
        db = self.SessionLocal()
        try:
            # 检查是否有无效的 JSON 数据
            portfolios_with_invalid_json = db.query(Portfolio).filter(
                Portfolio.tech_stack.is_(None)
            ).count()
            if portfolios_with_invalid_json > 0:
                issues.append(f"发现 {portfolios_with_invalid_json} 个作品的技术栈字段为空")
            
            blogs_with_invalid_json = db.query(Blog).filter(
                Blog.tags.is_(None)
            ).count()
            if blogs_with_invalid_json > 0:
                issues.append(f"发现 {blogs_with_invalid_json} 个博客的标签字段为空")
            
        except Exception as e:
            issues.append(f"数据完整性检查失败: {e}")
        finally:
            db.close()
        
        if issues:
            print("发现以下问题:")
            for issue in issues:
                print(f"  - {issue}")
            return False
        else:
            print("数据库健康状态良好")
            return True

def run_migrations():
    """运行数据库迁移的入口函数"""
    migration = DatabaseMigration()
    migration.run_all_migrations()

def check_health():
    """检查数据库健康状态的入口函数"""
    migration = DatabaseMigration()
    return migration.check_database_health()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "migrate":
            run_migrations()
        elif sys.argv[1] == "health":
            check_health()
        else:
            print("用法: python migrations.py [migrate|health]")
    else:
        run_migrations()