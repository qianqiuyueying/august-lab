#!/usr/bin/env python3
"""
产品文件管理工具
用于维护和管理产品文件存储
"""

import sys
import argparse
from pathlib import Path
from app.services import product_file_service
from app.database import get_db
from app.models import Product as ProductModel


def list_products():
    """列出所有产品"""
    db = next(get_db())
    products = db.query(ProductModel).all()
    
    print(f"共找到 {len(products)} 个产品:")
    print("-" * 80)
    
    for product in products:
        status = "✓" if product.is_published else "○"
        # 检查文件是否存在（基于ID的固定路径）
        product_dir = product_file_service.get_product_directory(product.id)
        file_status = "有文件" if product_dir.exists() else "无文件"
        
        print(f"{status} ID: {product.id:3d} | {product.title:30s} | {product.product_type:8s} | {file_status}")
    
    db.close()


def verify_all_products():
    """验证所有产品的文件完整性"""
    db = next(get_db())
    # 获取所有产品，检查文件是否存在（基于ID）
    all_products = db.query(ProductModel).all()
    products = [p for p in all_products if product_file_service.get_product_directory(p.id).exists()]
    
    print(f"验证 {len(products)} 个有文件的产品:")
    print("-" * 80)
    
    valid_count = 0
    
    for product in products:
        is_valid, message = product_file_service.verify_product_integrity(product.id)
        status = "✓" if is_valid else "✗"
        
        print(f"{status} ID: {product.id:3d} | {product.title:30s} | {message}")
        
        if is_valid:
            valid_count += 1
    
    print("-" * 80)
    print(f"验证完成: {valid_count}/{len(products)} 个产品文件完整")
    
    db.close()


def show_storage_stats():
    """显示存储统计信息"""
    stats = product_file_service.get_storage_stats()
    
    print("存储统计信息:")
    print("-" * 40)
    print(f"存储路径: {stats['storage_path']}")
    print(f"产品数量: {stats['total_products']}")
    print(f"文件数量: {stats['total_files']}")
    print(f"总大小: {format_size(stats['total_size'])}")


def show_product_details(product_id: int):
    """显示产品详细信息"""
    db = next(get_db())
    product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    
    if not product:
        print(f"产品 ID {product_id} 不存在")
        db.close()
        return
    
    print(f"产品详细信息 (ID: {product_id}):")
    print("-" * 50)
    print(f"标题: {product.title}")
    print(f"描述: {product.description or '无'}")
    print(f"类型: {product.product_type}")
    print(f"版本: {product.version}")
    print(f"入口文件: {product.entry_file}")
    print(f"发布状态: {'已发布' if product.is_published else '未发布'}")
    print(f"推荐状态: {'推荐' if product.is_featured else '普通'}")
    # 使用基于ID的固定路径
    product_dir = product_file_service.get_product_directory(product_id)
    print(f"文件路径: {str(product_dir) if product_dir.exists() else '无'}")
    
    if product_dir.exists():
        # 显示文件信息
        file_info = product_file_service.get_product_files(product_id)
        files = file_info.get('files', [])
        
        print(f"\n文件信息:")
        print(f"文件数量: {len(files)}")
        print(f"总大小: {format_size(file_info.get('total_size', 0))}")
        
        if files:
            print("\n文件列表:")
            for file in files[:10]:  # 只显示前10个文件
                print(f"  {file['path']} ({format_size(file['size'])})")
            
            if len(files) > 10:
                print(f"  ... 还有 {len(files) - 10} 个文件")
        
        # 验证完整性
        is_valid, message = product_file_service.verify_product_integrity(product_id)
        print(f"\n完整性验证: {'✓ ' + message if is_valid else '✗ ' + message}")
    
    db.close()


def cleanup_orphaned_files():
    """清理孤立的文件（没有对应产品记录的文件）"""
    db = next(get_db())
    
    # 获取所有产品ID
    product_ids = set(str(p.id) for p in db.query(ProductModel.id).all())
    
    # 检查文件系统中的目录
    storage_path = Path(product_file_service.base_dir)
    if not storage_path.exists():
        print("存储目录不存在")
        db.close()
        return
    
    orphaned_dirs = []
    for item in storage_path.iterdir():
        if item.is_dir() and item.name.isdigit():
            if item.name not in product_ids:
                orphaned_dirs.append(item)
    
    if not orphaned_dirs:
        print("没有发现孤立的文件")
        db.close()
        return
    
    print(f"发现 {len(orphaned_dirs)} 个孤立的文件目录:")
    for dir_path in orphaned_dirs:
        size = sum(f.stat().st_size for f in dir_path.rglob('*') if f.is_file())
        print(f"  {dir_path.name} ({format_size(size)})")
    
    if input("\n是否删除这些孤立文件? (y/N): ").lower() == 'y':
        import shutil
        for dir_path in orphaned_dirs:
            try:
                shutil.rmtree(dir_path)
                print(f"✓ 已删除: {dir_path.name}")
            except Exception as e:
                print(f"✗ 删除失败 {dir_path.name}: {e}")
    
    db.close()


def format_size(size_bytes: int) -> str:
    """格式化文件大小"""
    if size_bytes == 0:
        return "0 B"
    
    units = ['B', 'KB', 'MB', 'GB']
    unit_index = 0
    size = float(size_bytes)
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    return f"{size:.1f} {units[unit_index]}"


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="产品文件管理工具")
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 列出产品
    subparsers.add_parser('list', help='列出所有产品')
    
    # 验证产品
    subparsers.add_parser('verify', help='验证所有产品文件完整性')
    
    # 存储统计
    subparsers.add_parser('stats', help='显示存储统计信息')
    
    # 产品详情
    detail_parser = subparsers.add_parser('detail', help='显示产品详细信息')
    detail_parser.add_argument('product_id', type=int, help='产品ID')
    
    # 清理孤立文件
    subparsers.add_parser('cleanup', help='清理孤立的文件')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'list':
            list_products()
        elif args.command == 'verify':
            verify_all_products()
        elif args.command == 'stats':
            show_storage_stats()
        elif args.command == 'detail':
            show_product_details(args.product_id)
        elif args.command == 'cleanup':
            cleanup_orphaned_files()
    
    except KeyboardInterrupt:
        print("\n操作已取消")
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()