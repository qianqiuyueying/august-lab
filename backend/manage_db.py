#!/usr/bin/env python3
"""
数据库管理脚本
用于数据库的初始化、重置和迁移操作
"""

import argparse
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database_init import init_database, reset_database
from app.database import engine, Base
from app.migrations import run_migrations, check_health
from sqlalchemy import text

def create_tables():
    """仅创建数据库表，不添加示例数据"""
    print("正在创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("数据库表创建完成")

def drop_tables():
    """删除所有数据库表"""
    print("正在删除数据库表...")
    Base.metadata.drop_all(bind=engine)
    print("数据库表删除完成")

def show_tables():
    """显示数据库中的所有表"""
    print("数据库表列表:")
    with engine.connect() as conn:
        result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
        tables = result.fetchall()
        if tables:
            for table in tables:
                print(f"  - {table[0]}")
        else:
            print("  (无表)")

def show_stats():
    """显示数据库统计信息"""
    print("数据库统计信息:")
    
    from app.models import Portfolio, Blog, Profile, Session
    from app.database import SessionLocal
    
    db = SessionLocal()
    try:
        portfolio_count = db.query(Portfolio).count()
        blog_count = db.query(Blog).count()
        published_blog_count = db.query(Blog).filter(Blog.is_published == True).count()
        profile_count = db.query(Profile).count()
        session_count = db.query(Session).filter(Session.is_active == True).count()
        
        print(f"  作品数量: {portfolio_count}")
        print(f"  博客总数: {blog_count}")
        print(f"  已发布博客: {published_blog_count}")
        print(f"  个人信息: {profile_count}")
        print(f"  活跃会话: {session_count}")
    except Exception as e:
        print(f"  获取统计信息失败: {e}")
    finally:
        db.close()

def main():
    parser = argparse.ArgumentParser(description="数据库管理工具")
    parser.add_argument("command", choices=[
        "init", "reset", "create", "drop", "tables", "stats", "migrate", "health"
    ], help="要执行的命令")
    
    args = parser.parse_args()
    
    try:
        if args.command == "init":
            init_database()
        elif args.command == "reset":
            reset_database()
        elif args.command == "create":
            create_tables()
        elif args.command == "drop":
            drop_tables()
        elif args.command == "tables":
            show_tables()
        elif args.command == "stats":
            show_stats()
        elif args.command == "migrate":
            run_migrations()
        elif args.command == "health":
            check_health()
    except Exception as e:
        print(f"执行命令时出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()