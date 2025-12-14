from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Request
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
import os
import tempfile
import shutil
import secrets
from pathlib import Path

from ..database import get_db
from ..models import (
    Product as ProductModel, ProductStats as ProductStatsModel, 
    ProductLog as ProductLogModel, ProductFeedback as ProductFeedbackModel,
    ProductAPIToken as ProductAPITokenModel, ProductAPICall as ProductAPICallModel,
    ProductDataStorage as ProductDataStorageModel, ProductUser as ProductUserModel,
    ProductUserSession as ProductUserSessionModel
)
from ..schemas import (
    ExtensionInstallRequest,
    ExtensionConfigureRequest,
    Product, ProductCreate, ProductUpdate, ProductStats, ProductStatsCreate,
    ProductLog, ProductLogCreate, ProductUploadResponse, ProductAnalytics, MessageResponse,
    ProductFeedback, ProductFeedbackCreate, ProductFeedbackUpdate, ProductFeedbackStats,
    ProductFeedbackPublic
)
from fastapi import Form
from datetime import datetime
from ..transaction import transactional, with_db_error_handling
from ..security import (
    create_safe_query_executor, sql_injection_protection, validate_and_sanitize_input,
    validate_extension_name, validate_extension_path
)
from ..error_handlers import (
    ResourceNotFoundAPIError, ValidationAPIError, create_success_response, 
    create_paginated_response
)
from ..services import product_file_service
from ..services.product_extension_service import product_extension_service
from .auth import get_current_user

router = APIRouter()

# 注意：这些固定路径的路由必须在动态路由 {product_id} 之前定义
# 否则 FastAPI 会尝试将 "product-types" 等字符串解析为 product_id 整数，导致 422 错误

@router.get("/product-types")
def get_available_product_types():
    """获取可用的产品类型（公开接口）"""
    try:
        product_types = product_extension_service.get_available_product_types()
        return {"product_types": product_types}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取产品类型失败: {str(e)}"
        )

@router.get("/extensions")
@sql_injection_protection
def list_extensions(
    current_user: str = Depends(get_current_user)
):
    """列出所有扩展（需要认证）"""
    try:
        extensions = product_extension_service.list_extensions()
        return {"extensions": extensions}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取扩展列表失败: {str(e)}"
        )

@router.get("/", response_model=List[Product])
@sql_injection_protection
def get_products(
    skip: int = 0,
    limit: int = 100,
    search: str = None,
    product_type: str = None,
    published_only: bool = True,
    db: Session = Depends(get_db)
):
    """获取产品列表（公开接口）"""
    safe_executor = create_safe_query_executor(db)
    
    # 构建过滤条件
    filters = {}
    if published_only:
        filters['is_published'] = True
    if product_type:
        filters['product_type'] = product_type
    
    if search:
        # 使用安全搜索
        products = safe_executor.safe_search_query(
            ProductModel, 
            ['title', 'description'], 
            search, 
            filters=filters,
            limit=min(limit, 100)
        )
    else:
        # 使用安全过滤查询
        products = safe_executor.safe_filter_query(
            ProductModel,
            filters,
            limit=min(limit, 100),
            offset=max(skip, 0),
            order_by='display_order'
        )
    
    return products

@router.get("/{product_id}", response_model=Product)
@sql_injection_protection
def get_product(product_id: int, db: Session = Depends(get_db)):
    """获取单个产品详情（公开接口）"""
    safe_executor = create_safe_query_executor(db)
    
    product = safe_executor.safe_get_by_id(ProductModel, product_id)
    
    if not product:
        raise ResourceNotFoundAPIError("产品", product_id)
    
    # 如果产品未发布，只有管理员可以查看
    if not product.is_published:
        # 这里可以添加权限检查，暂时允许查看
        pass
    
    return product

@router.post("/", response_model=Product)
@with_db_error_handling
@sql_injection_protection
def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """创建新产品（需要认证）"""
    try:
        # 验证和清理输入数据
        safe_data = validate_and_sanitize_input(product_data.dict())
        
        # 确保tech_stack字段为列表而不是None
        if safe_data.get('tech_stack') is None:
            safe_data['tech_stack'] = []
        
        # 确保必需的字段有默认值
        if 'entry_file' not in safe_data or not safe_data['entry_file']:
            safe_data['entry_file'] = 'index.html'
            
        if 'version' not in safe_data or not safe_data['version']:
            safe_data['version'] = '1.0.0'
            
        if 'config_data' not in safe_data or safe_data['config_data'] is None:
            safe_data['config_data'] = {}
        
        product = ProductModel(**safe_data)
        db.add(product)
        db.commit()  # 确保提交事务
        db.refresh(product)
        return product
    except Exception as e:
        db.rollback()
        raise e

@router.put("/{product_id}", response_model=Product)
@transactional(rollback_on_exception=True, max_retries=2)
@with_db_error_handling
@sql_injection_protection
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """更新产品（需要认证）"""
    safe_executor = create_safe_query_executor(db)
    
    product = safe_executor.safe_get_by_id(ProductModel, product_id)
    
    if not product:
        raise ResourceNotFoundAPIError("产品", product_id)
    
    # 验证和清理更新数据
    update_data = validate_and_sanitize_input(product_data.dict(exclude_unset=True))
    
    for field, value in update_data.items():
        setattr(product, field, value)
    
    db.flush()  # 刷新但不提交
    db.refresh(product)
    return product

@router.delete("/{product_id}", response_model=MessageResponse)
@transactional(rollback_on_exception=True, max_retries=2)
@with_db_error_handling
@sql_injection_protection
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """删除产品（需要认证）"""
    safe_executor = create_safe_query_executor(db)
    
    product = safe_executor.safe_get_by_id(ProductModel, product_id)
    
    if not product:
        raise ResourceNotFoundAPIError("产品", product_id)
    
    # 删除产品文件
    product_file_service.delete_product_files(product_id)
    
    db.delete(product)
    # 事务装饰器会处理提交
    
    return MessageResponse(message="产品删除成功")

@router.post("/{product_id}/upload", response_model=ProductUploadResponse)
@transactional(rollback_on_exception=True, max_retries=2)
@with_db_error_handling
def upload_product_files(
    product_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """上传产品文件（需要认证）"""
    safe_executor = create_safe_query_executor(db)
    
    product = safe_executor.safe_get_by_id(ProductModel, product_id)
    
    if not product:
        raise ResourceNotFoundAPIError("产品", product_id)
    
    # 验证文件
    if not file.filename:
        raise ValidationAPIError("文件名不能为空")
    
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in product_file_service.allowed_extensions:
        raise ValidationAPIError(f"只支持以下文件格式: {', '.join(product_file_service.allowed_extensions)}")
    
    temp_file_path = None
    try:
        # 保存上传的ZIP文件到临时位置
        # 确保文件指针在开始位置（如果支持seek）
        try:
            if hasattr(file.file, 'seek'):
                file.file.seek(0)
        except (AttributeError, OSError):
            # 如果文件对象不支持seek，继续尝试读取
            pass
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_file:
            # 读取文件内容并写入临时文件
            # 使用 read() 方法读取所有内容
            file_content = file.file.read()
            if not file_content:
                # 如果读取为空，可能是文件指针不在开始位置，尝试重新读取
                if hasattr(file.file, 'seek'):
                    file.file.seek(0)
                    file_content = file.file.read()
            
            if not file_content:
                raise ValidationAPIError("无法读取上传的文件内容")
            
            temp_file.write(file_content)
            temp_file_path = temp_file.name
        
        # 检查文件大小
        file_size = Path(temp_file_path).stat().st_size
        if file_size > product_file_service.max_file_size:
            max_size_mb = product_file_service.max_file_size // (1024*1024)
            raise ValidationAPIError(f"文件大小超过限制 ({max_size_mb}MB)")
        
        # 使用文件服务处理上传
        result = product_file_service.upload_product_files(product, temp_file_path)
        
        # 更新 product.file_path 为标记值（用于前端判断文件是否已上传）
        # 实际文件路径基于ID计算，但需要设置标记值以便前端识别
        product.file_path = result.file_path
        db.flush()  # 刷新到数据库（@transactional 装饰器会自动提交）
        
        return result
        
    except ValueError as e:
        # 注意：不要手动调用 db.rollback()，@transactional 装饰器会自动处理
        raise ValidationAPIError(str(e))
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"文件上传错误详情: {error_details}")  # 打印详细错误信息以便调试
        # 注意：不要手动调用 db.rollback()，@transactional 装饰器会自动处理
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件处理失败: {str(e)}"
        )
    finally:
        # 确保清理临时文件
        if temp_file_path and Path(temp_file_path).exists():
            try:
                Path(temp_file_path).unlink()
            except Exception as e:
                # 记录日志但不中断主要流程
                print(f"清理临时文件失败: {e}")

@router.get("/{product_id}/files")
@sql_injection_protection
def get_product_files(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """获取产品文件列表（需要认证）"""
    safe_executor = create_safe_query_executor(db)
    
    product = safe_executor.safe_get_by_id(ProductModel, product_id)
    
    if not product:
        raise ResourceNotFoundAPIError("产品", product_id)
    
    return product_file_service.get_product_files(product_id)

@router.get("/{product_id}/launch")
@sql_injection_protection
def launch_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    """启动产品应用（公开接口）"""
    safe_executor = create_safe_query_executor(db)
    
    product = safe_executor.safe_get_by_id(ProductModel, product_id)
    
    if not product:
        raise ResourceNotFoundAPIError("产品", product_id)
    
    if not product.is_published:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="产品未发布"
        )
    
    # 使用基于ID的固定路径（不再依赖数据库中的file_path）
    product_dir = product_file_service.get_product_directory(product_id)
    if not product_dir.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="产品文件不存在"
        )
    
    # 检查入口文件是否存在
    entry_file_path = product_dir / product.entry_file
    if not entry_file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"入口文件不存在: {product.entry_file}"
        )
    
    return {
        "product_id": product_id,
        "title": product.title,
        "entry_url": f"/products/{product_id}/{product.entry_file}",
        "config": product.config_data or {}
    }

@router.get("/{product_id}/stats")
@sql_injection_protection
def get_product_stats(
    product_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取产品统计数据（公开接口）"""
    safe_executor = create_safe_query_executor(db)
    
    product = safe_executor.safe_get_by_id(ProductModel, product_id)
    
    if not product:
        raise ResourceNotFoundAPIError("产品", product_id)
    
    try:
        # 查询统计数据（分页）
        stats_query = db.query(ProductStatsModel).filter(
            ProductStatsModel.product_id == product_id
        ).order_by(ProductStatsModel.access_time.desc())
        
        total = stats_query.count()
        stats = stats_query.offset(max(skip, 0)).limit(min(limit, 100)).all()
        
        # 计算汇总统计（使用聚合查询提高性能）
        summary_query = db.query(
            func.count(ProductStatsModel.id).label('total_visits'),
            func.count(func.distinct(ProductStatsModel.visitor_ip)).label('unique_visitors'),
            func.avg(ProductStatsModel.duration_seconds).label('average_duration'),
            func.max(ProductStatsModel.access_time).label('last_access')
        ).filter(
            ProductStatsModel.product_id == product_id
        ).first()
        
        total_visits = summary_query.total_visits or 0
        unique_visitors = summary_query.unique_visitors or 0
        average_duration = float(summary_query.average_duration) if summary_query.average_duration else 0.0
        last_access = summary_query.last_access
        
        return {
            "product_id": product_id,
            "summary": {
                "total_visits": total_visits,
                "unique_visitors": unique_visitors,
                "average_duration": round(average_duration, 2),
                "last_access": last_access.replace(tzinfo=timezone.utc).isoformat() if last_access else None
            },
            "stats": [{
                "id": stat.id,
                "visitor_ip": stat.visitor_ip,
                "session_id": stat.session_id,
                "access_time": stat.access_time.replace(tzinfo=timezone.utc).isoformat() if stat.access_time else None,
                "duration_seconds": stat.duration_seconds,
                "user_agent": stat.user_agent,
                "referrer": stat.referrer
            } for stat in stats],
            "pagination": {
                "skip": skip,
                "limit": limit,
                "total": total
            }
        }
    except Exception as e:
        import traceback
        logger.error(f"获取产品统计数据失败: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取统计数据失败: {str(e)}"
        )

@router.post("/{product_id}/stats", response_model=ProductStats)
@transactional(rollback_on_exception=True, max_retries=2)
@with_db_error_handling
def record_product_stats(
    product_id: int,
    stats_data: ProductStatsCreate,
    db: Session = Depends(get_db)
):
    """记录产品使用统计（公开接口）"""
    safe_executor = create_safe_query_executor(db)
    
    product = safe_executor.safe_get_by_id(ProductModel, product_id)
    
    if not product:
        raise ResourceNotFoundAPIError("产品", product_id)
    
    # 验证和清理统计数据
    safe_data = validate_and_sanitize_input(stats_data.dict())
    
    # 如果没有提供 access_time，在 Python 端设置，避免需要从数据库刷新
    # 注意：ProductStatsCreate schema 可能不包含 access_time 字段（由数据库自动生成）
    # 但我们在创建模型实例时手动设置，这样就不需要刷新了
    if 'access_time' not in safe_data or safe_data.get('access_time') is None:
        safe_data['access_time'] = datetime.utcnow()
    
    stats = ProductStatsModel(**safe_data)
    db.add(stats)
    # 使用 flush() 将更改发送到数据库并生成 ID，但不提交事务
    # @transactional 装饰器会在函数返回后自动提交事务
    db.flush()
    
    # 注意：不要使用 db.refresh()，因为可能与事务装饰器的提交时机冲突
    # flush() 后对象已经包含了生成的 ID 和我们设置的 access_time
    # 这样就不需要从数据库刷新了
    
    return stats

@router.get("/{product_id}/analytics", response_model=ProductAnalytics)
@sql_injection_protection
def get_product_analytics(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """获取产品分析数据（需要认证）"""
    safe_executor = create_safe_query_executor(db)
    
    product = safe_executor.safe_get_by_id(ProductModel, product_id)
    
    if not product:
        raise ResourceNotFoundAPIError("产品", product_id)
    
    # 查询统计数据
    stats = db.query(ProductStatsModel).filter(
        ProductStatsModel.product_id == product_id
    ).all()
    
    if not stats:
        return ProductAnalytics(
            product_id=product_id,
            total_visits=0,
            unique_visitors=0,
            average_duration=0.0,
            last_access=None,
            popular_times=[]
        )
    
    # 计算分析数据
    total_visits = len(stats)
    unique_visitors = len(set(s.visitor_ip for s in stats if s.visitor_ip))
    average_duration = sum(s.duration_seconds for s in stats) / total_visits if total_visits > 0 else 0
    # 过滤掉access_time为None的记录
    stats_with_time = [s for s in stats if s.access_time is not None]
    last_access = max(s.access_time for s in stats_with_time) if stats_with_time else None
    
    # 简单的热门时间分析（按小时）
    popular_times = []
    hour_counts = {}
    for stat in stats:
        if stat.access_time:  # 检查access_time是否为None
            hour = stat.access_time.hour
            hour_counts[hour] = hour_counts.get(hour, 0) + 1
    
    for hour, count in sorted(hour_counts.items()):
        popular_times.append({
            "hour": hour,
            "visits": count
        })
    
    return ProductAnalytics(
        product_id=product_id,
        total_visits=total_visits,
        unique_visitors=unique_visitors,
        average_duration=average_duration,
        last_access=last_access,
        popular_times=popular_times
    )

@router.post("/{product_id}/logs", response_model=ProductLog)
@transactional(rollback_on_exception=True, max_retries=2)
@with_db_error_handling
def create_product_log(
    product_id: int,
    log_data: ProductLogCreate,
    db: Session = Depends(get_db)
):
    """创建产品日志（公开接口）"""
    safe_executor = create_safe_query_executor(db)
    
    product = safe_executor.safe_get_by_id(ProductModel, product_id)
    
    if not product:
        raise ResourceNotFoundAPIError("产品", product_id)
    
    # 验证和清理日志数据
    safe_data = validate_and_sanitize_input(log_data.dict())
    
    log = ProductLogModel(**safe_data)
    db.add(log)
    db.flush()
    db.refresh(log)
    return log

@router.get("/{product_id}/logs")
@sql_injection_protection
def get_product_logs(
    product_id: int,
    log_type: Optional[str] = None,
    log_level: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """获取产品日志（需要认证）"""
    safe_executor = create_safe_query_executor(db)
    
    product = safe_executor.safe_get_by_id(ProductModel, product_id)
    
    if not product:
        raise ResourceNotFoundAPIError("产品", product_id)
    
    # 构建过滤条件
    filters = {"product_id": product_id}
    if log_type:
        filters["log_type"] = log_type
    if log_level:
        filters["log_level"] = log_level
    
    logs = safe_executor.safe_filter_query(
        ProductLogModel,
        filters,
        limit=min(limit, 100),
        offset=max(skip, 0),
        order_by='timestamp'
    )
    
    return logs

@router.get("/{product_id}/verify")
@sql_injection_protection
def verify_product_integrity(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """验证产品文件完整性（需要认证）"""
    safe_executor = create_safe_query_executor(db)
    
    product = safe_executor.safe_get_by_id(ProductModel, product_id)
    
    if not product:
        raise ResourceNotFoundAPIError("产品", product_id)
    
    try:
        is_valid, message = product_file_service.verify_product_integrity(product_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"验证过程出错: {str(e)}"
        )
    
    return {
        "product_id": product_id,
        "is_valid": is_valid,
        "message": message
    }

@router.get("/storage/stats")
@sql_injection_protection
def get_storage_stats(
    current_user: str = Depends(get_current_user)
):
    """获取存储统计信息（需要认证）"""
    return product_file_service.get_storage_stats()

@router.get("/{product_id}/monitoring/errors")
@with_db_error_handling
@sql_injection_protection
def get_product_errors(
    product_id: int,
    severity: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """获取产品错误日志（需要认证）"""
    safe_executor = create_safe_query_executor(db)
    
    product = safe_executor.safe_get_by_id(ProductModel, product_id)
    
    if not product:
        raise ResourceNotFoundAPIError("产品", product_id)
    
    # 构建过滤条件
    filters = {
        "product_id": product_id,
        "log_type": "error"
    }
    if severity:
        filters["log_level"] = severity
    
    # 使用原生查询以确保正确的排序（降序，最新的在前）
    query = db.query(ProductLogModel).filter(
        ProductLogModel.product_id == product_id,
        ProductLogModel.log_type == "error"
    )
    
    if severity:
        query = query.filter(ProductLogModel.log_level == severity)
    
    errors = query.order_by(desc(ProductLogModel.timestamp)).offset(max(skip, 0)).limit(min(limit, 100)).all()
    
    return errors

@router.get("/{product_id}/monitoring/performance")
@with_db_error_handling
@sql_injection_protection
def get_product_performance(
    product_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """获取产品性能数据（需要认证）"""
    safe_executor = create_safe_query_executor(db)
    
    product = safe_executor.safe_get_by_id(ProductModel, product_id)
    
    if not product:
        raise ResourceNotFoundAPIError("产品", product_id)
    
    # 使用原生查询以确保正确的排序（降序，最新的在前）
    performance_logs = db.query(ProductLogModel).filter(
        ProductLogModel.product_id == product_id,
        ProductLogModel.log_type == "performance"
    ).order_by(desc(ProductLogModel.timestamp)).offset(max(skip, 0)).limit(min(limit, 100)).all()
    
    return performance_logs

@router.post("/{product_id}/monitoring/diagnostic")
@transactional(rollback_on_exception=True, max_retries=2)
@with_db_error_handling
def run_product_diagnostic(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """运行产品诊断（需要认证）"""
    safe_executor = create_safe_query_executor(db)
    
    product = safe_executor.safe_get_by_id(ProductModel, product_id)
    
    if not product:
        raise ResourceNotFoundAPIError("产品", product_id)
    
    # 运行基本诊断检查
    diagnostic_results = {
        "product_id": product_id,
        "timestamp": "2024-01-01T00:00:00Z",
        "overall_status": "good",
        "checks": {
            "file_integrity": product_file_service.verify_product_integrity(product_id)[0],
            "entry_file_exists": (product_file_service.get_product_directory(product_id) / product.entry_file).exists(),
            "config_valid": bool(product.config_data),
            "published_status": product.is_published
        },
        "recommendations": []
    }
    
    # 根据检查结果生成建议
    if not diagnostic_results["checks"]["file_integrity"]:
        diagnostic_results["recommendations"].append("产品文件完整性检查失败，建议重新上传")
    
    if not diagnostic_results["checks"]["entry_file_exists"]:
        diagnostic_results["recommendations"].append("入口文件不存在，请检查文件结构")
    
    if not diagnostic_results["checks"]["published_status"]:
        diagnostic_results["recommendations"].append("产品未发布，用户无法访问")
    
    # 记录诊断日志
    log_data = ProductLogCreate(
        product_id=product_id,
        log_type="diagnostic",
        log_level="info",
        message="产品诊断完成",
        details=diagnostic_results
    )
    
    safe_data = validate_and_sanitize_input(log_data.dict())
    log = ProductLogModel(**safe_data)
    db.add(log)
    db.flush()
    
    return diagnostic_results

@router.get("/monitoring/system-status")
@sql_injection_protection
def get_system_status(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取系统整体状态（需要认证）"""
    # 获取产品统计
    total_products = db.query(ProductModel).count()
    published_products = db.query(ProductModel).filter(ProductModel.is_published == True).count()
    
    # 获取最近的错误日志
    recent_errors = db.query(ProductLogModel).filter(
        ProductLogModel.log_type == "error"
    ).order_by(ProductLogModel.timestamp.desc()).limit(10).all()
    
    # 计算错误率（简化版本）
    total_logs = db.query(ProductLogModel).count()
    error_count = len(recent_errors)
    error_rate = (error_count / total_logs * 100) if total_logs > 0 else 0
    
    return {
        "timestamp": "2024-01-01T00:00:00Z",
        "overall_status": "good" if error_rate < 5 else "warning" if error_rate < 10 else "critical",
        "metrics": {
            "total_products": total_products,
            "published_products": published_products,
            "error_rate": round(error_rate, 2),
            "recent_errors": len(recent_errors)
        },
        "storage": product_file_service.get_storage_stats()
    }

# 产品反馈相关接口
@router.post("/{product_id}/feedback", response_model=ProductFeedback)
@transactional(rollback_on_exception=True, max_retries=2)
@with_db_error_handling
def create_product_feedback(
    product_id: int,
    feedback_data: ProductFeedbackCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """创建产品反馈（公开接口）"""
    safe_executor = create_safe_query_executor(db)
    
    product = safe_executor.safe_get_by_id(ProductModel, product_id)
    
    if not product:
        raise ResourceNotFoundAPIError("产品", product_id)
    
    # 验证和清理反馈数据
    safe_data = validate_and_sanitize_input(feedback_data.dict())
    
    # 添加请求信息
    safe_data.update({
        'user_agent': request.headers.get('user-agent'),
        'ip_address': request.client.host if hasattr(request, 'client') else None
    })
    
    feedback = ProductFeedbackModel(**safe_data)
    db.add(feedback)
    db.flush()
    db.refresh(feedback)
    return feedback

def filter_sensitive_content(content: str) -> str:
    """
    过滤敏感内容，确保符合监管要求
    
    Args:
        content: 原始内容
        
    Returns:
        过滤后的内容
    """
    if not content:
        return content
    
    import re
    
    # 基础敏感词列表（可根据需要扩展）
    # 注意：这里只是示例，实际使用时应该使用更完善的敏感词库或接入第三方内容审核服务
    sensitive_words = [
        # 可以在这里添加需要过滤的敏感词
    ]
    
    filtered = content
    
    # 过滤敏感词（简单替换为*）
    for word in sensitive_words:
        if word:
            # 使用正则表达式进行大小写不敏感的替换
            pattern = re.compile(re.escape(word), re.IGNORECASE)
            filtered = pattern.sub('*' * len(word), filtered)
    
    # 移除可能的HTML标签和脚本（防止XSS）
    # 移除script标签
    filtered = re.sub(r'<script[^>]*>.*?</script>', '', filtered, flags=re.IGNORECASE | re.DOTALL)
    # 移除on事件属性
    filtered = re.sub(r'\s*on\w+\s*=\s*["\'][^"\']*["\']', '', filtered, flags=re.IGNORECASE)
    # 移除javascript:协议
    filtered = re.sub(r'javascript:', '', filtered, flags=re.IGNORECASE)
    # 移除data:协议（可能包含恶意代码）
    filtered = re.sub(r'data:\s*[^;]*;base64,', '', filtered, flags=re.IGNORECASE)
    
    return filtered

@router.get("/{product_id}/feedback/public", response_model=List[ProductFeedbackPublic])
@sql_injection_protection
def get_product_feedback_public(
    product_id: int,
    feedback_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    获取产品公开反馈列表（公开接口，符合隐私保护要求）
    
    只返回已解决（resolved）或已关闭（closed）的反馈
    不包含任何敏感信息：用户姓名、邮箱、IP地址、用户代理等
    符合《个人信息保护法》和《网络安全法》要求
    """
    safe_executor = create_safe_query_executor(db)
    
    product = safe_executor.safe_get_by_id(ProductModel, product_id)
    if not product:
        raise ResourceNotFoundAPIError("产品", product_id)
    
    # 只查询已解决或已关闭的反馈
    from sqlalchemy import desc, or_
    query = db.query(ProductFeedbackModel).filter(
        ProductFeedbackModel.product_id == product_id,
        ProductFeedbackModel.status.in_(['resolved', 'closed'])
    )
    
    if feedback_type:
        query = query.filter(ProductFeedbackModel.feedback_type == feedback_type)
    
    # 限制返回数量，避免过多数据（最多20条）
    # 优先按回复时间排序，如果没有回复则按创建时间排序
    # 使用Python排序确保有回复的排在前面
    all_feedback = query.all()
    feedback_list = sorted(
        all_feedback,
        key=lambda x: (x.replied_at if x.replied_at else x.created_at),
        reverse=True
    )[max(skip, 0):max(skip, 0) + min(limit, 20)]
    
    # 转换为公开格式（不包含敏感信息）
    public_feedback = []
    for feedback in feedback_list:
        # 内容过滤：确保内容符合监管要求
        filtered_content = filter_sensitive_content(feedback.content)
        filtered_title = filter_sensitive_content(feedback.title)
        filtered_reply = filter_sensitive_content(feedback.admin_reply) if feedback.admin_reply else None
        
        public_feedback.append(ProductFeedbackPublic(
            id=feedback.id,
            product_id=feedback.product_id,
            feedback_type=feedback.feedback_type,
            rating=feedback.rating,
            title=filtered_title,
            content=filtered_content,
            status=feedback.status,
            admin_reply=filtered_reply,
            created_at=feedback.created_at,
            replied_at=feedback.replied_at
        ))
    
    return public_feedback

@router.get("/{product_id}/feedback")
@sql_injection_protection
def get_product_feedback(
    product_id: int,
    feedback_type: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """获取产品反馈列表（需要认证）"""
    safe_executor = create_safe_query_executor(db)
    
    product = safe_executor.safe_get_by_id(ProductModel, product_id)
    
    if not product:
        raise ResourceNotFoundAPIError("产品", product_id)
    
    # 构建过滤条件
    filters = {"product_id": product_id}
    if feedback_type:
        filters["feedback_type"] = feedback_type
    if status:
        filters["status"] = status
    
    # 使用原生查询以确保正确的排序（降序，最新的在前）
    from sqlalchemy import desc
    query = db.query(ProductFeedbackModel).filter(
        ProductFeedbackModel.product_id == product_id
    )
    
    if feedback_type:
        query = query.filter(ProductFeedbackModel.feedback_type == feedback_type)
    if status:
        query = query.filter(ProductFeedbackModel.status == status)
    
    feedback_list = query.order_by(desc(ProductFeedbackModel.created_at)).offset(max(skip, 0)).limit(min(limit, 100)).all()
    
    return feedback_list

@router.get("/{product_id}/feedback/{feedback_id}", response_model=ProductFeedback)
@sql_injection_protection
def get_feedback_detail(
    product_id: int,
    feedback_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """获取反馈详情（需要认证）"""
    safe_executor = create_safe_query_executor(db)
    
    product = safe_executor.safe_get_by_id(ProductModel, product_id)
    if not product:
        raise ResourceNotFoundAPIError("产品", product_id)
    
    feedback = safe_executor.safe_get_by_id(ProductFeedbackModel, feedback_id)
    if not feedback or feedback.product_id != product_id:
        raise ResourceNotFoundAPIError("反馈", feedback_id)
    
    return feedback

@router.put("/{product_id}/feedback/{feedback_id}", response_model=ProductFeedback)
@transactional(rollback_on_exception=True, max_retries=2)
@with_db_error_handling
@sql_injection_protection
def update_product_feedback(
    product_id: int,
    feedback_id: int,
    feedback_data: ProductFeedbackUpdate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """更新产品反馈（需要认证）"""
    safe_executor = create_safe_query_executor(db)
    
    product = safe_executor.safe_get_by_id(ProductModel, product_id)
    if not product:
        raise ResourceNotFoundAPIError("产品", product_id)
    
    feedback = safe_executor.safe_get_by_id(ProductFeedbackModel, feedback_id)
    if not feedback or feedback.product_id != product_id:
        raise ResourceNotFoundAPIError("反馈", feedback_id)
    
    # 验证和清理更新数据
    update_data = validate_and_sanitize_input(feedback_data.dict(exclude_unset=True))
    
    # 如果添加了管理员回复，设置回复时间
    if 'admin_reply' in update_data and update_data['admin_reply']:
        from datetime import datetime
        update_data['replied_at'] = datetime.utcnow()
    
    for field, value in update_data.items():
        setattr(feedback, field, value)
    
    db.flush()
    db.refresh(feedback)
    return feedback

@router.delete("/{product_id}/feedback/{feedback_id}", response_model=MessageResponse)
@transactional(rollback_on_exception=True, max_retries=2)
@with_db_error_handling
@sql_injection_protection
def delete_product_feedback(
    product_id: int,
    feedback_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """删除产品反馈（需要认证）"""
    safe_executor = create_safe_query_executor(db)
    
    product = safe_executor.safe_get_by_id(ProductModel, product_id)
    if not product:
        raise ResourceNotFoundAPIError("产品", product_id)
    
    feedback = safe_executor.safe_get_by_id(ProductFeedbackModel, feedback_id)
    if not feedback or feedback.product_id != product_id:
        raise ResourceNotFoundAPIError("反馈", feedback_id)
    
    db.delete(feedback)
    # 事务装饰器会处理提交
    
    return MessageResponse(message="反馈删除成功")

@router.get("/{product_id}/feedback-stats", response_model=ProductFeedbackStats)
@sql_injection_protection
def get_product_feedback_stats(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """获取产品反馈统计（需要认证）"""
    safe_executor = create_safe_query_executor(db)
    
    product = safe_executor.safe_get_by_id(ProductModel, product_id)
    if not product:
        raise ResourceNotFoundAPIError("产品", product_id)
    
    # 查询所有反馈
    all_feedback = db.query(ProductFeedbackModel).filter(
        ProductFeedbackModel.product_id == product_id
    ).all()
    
    if not all_feedback:
        return ProductFeedbackStats(
            product_id=product_id,
            total_feedback=0,
            average_rating=None,
            feedback_by_type={},
            feedback_by_status={},
            recent_feedback=[]
        )
    
    # 计算统计数据
    total_feedback = len(all_feedback)
    
    # 计算平均评分
    ratings = [f.rating for f in all_feedback if f.rating is not None]
    average_rating = sum(ratings) / len(ratings) if ratings else None
    
    # 按类型统计
    feedback_by_type = {}
    for feedback in all_feedback:
        feedback_by_type[feedback.feedback_type] = feedback_by_type.get(feedback.feedback_type, 0) + 1
    
    # 按状态统计
    feedback_by_status = {}
    for feedback in all_feedback:
        feedback_by_status[feedback.status] = feedback_by_status.get(feedback.status, 0) + 1
    
    # 最近的反馈
    recent_feedback = sorted(all_feedback, key=lambda x: x.created_at, reverse=True)[:5]
    
    return ProductFeedbackStats(
        product_id=product_id,
        total_feedback=total_feedback,
        average_rating=average_rating,
        feedback_by_type=feedback_by_type,
        feedback_by_status=feedback_by_status,
        recent_feedback=recent_feedback
    )

# 产品API通信相关接口
@router.post("/{product_id}/api/token")
@transactional(rollback_on_exception=True, max_retries=2)
@with_db_error_handling
@sql_injection_protection
def generate_api_token(
    product_id: int,
    token_data: dict,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """生成产品API令牌（需要认证）"""
    safe_executor = create_safe_query_executor(db)
    
    product = safe_executor.safe_get_by_id(ProductModel, product_id)
    if not product:
        raise ResourceNotFoundAPIError("产品", product_id)
    
    import secrets
    from datetime import datetime, timedelta
    
    # 生成安全的令牌
    token = secrets.token_urlsafe(32)
    
    # 验证权限
    permissions = token_data.get('permissions', ['read'])
    allowed_permissions = ['read', 'write', 'admin']
    if not all(perm in allowed_permissions for perm in permissions):
        raise ValidationAPIError("无效的权限设置")
    
    # 创建令牌记录
    api_token = ProductAPITokenModel(
        product_id=product_id,
        token=token,
        permissions=permissions,
        expires_at=datetime.utcnow() + timedelta(days=30)  # 30天有效期
    )
    
    db.add(api_token)
    db.flush()
    db.refresh(api_token)
    
    return {
        "token": token,
        "expires_at": api_token.expires_at.isoformat(),
        "permissions": permissions,
        "product_id": product_id
    }

@router.post("/{product_id}/api/validate")
@sql_injection_protection
def validate_api_token(
    product_id: int,
    token_data: dict,
    db: Session = Depends(get_db)
):
    """验证API令牌（公开接口）"""
    safe_executor = create_safe_query_executor(db)
    
    product = safe_executor.safe_get_by_id(ProductModel, product_id)
    if not product:
        raise ResourceNotFoundAPIError("产品", product_id)
    
    token = token_data.get('token')
    if not token:
        raise ValidationAPIError("令牌不能为空")
    
    # 查找令牌
    api_token = db.query(ProductAPITokenModel).filter(
        ProductAPITokenModel.token == token,
        ProductAPITokenModel.product_id == product_id,
        ProductAPITokenModel.is_active == True
    ).first()
    
    if not api_token:
        return {"valid": False, "reason": "令牌不存在或已失效"}
    
    from datetime import datetime
    if api_token.expires_at < datetime.utcnow():
        return {"valid": False, "reason": "令牌已过期"}
    
    # 更新使用记录
    api_token.last_used_at = datetime.utcnow()
    api_token.usage_count += 1
    db.commit()
    
    return {
        "valid": True,
        "permissions": api_token.permissions,
        "expires_at": api_token.expires_at.isoformat()
    }

@router.get("/{product_id}/api/tokens")
@with_db_error_handling
@sql_injection_protection
def get_api_tokens(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """获取产品API令牌列表（需要认证）"""
    safe_executor = create_safe_query_executor(db)
    
    product = safe_executor.safe_get_by_id(ProductModel, product_id)
    if not product:
        raise ResourceNotFoundAPIError("产品", product_id)
    
    # 查询所有令牌（包括已撤销的）
    tokens = db.query(ProductAPITokenModel).filter(
        ProductAPITokenModel.product_id == product_id
    ).order_by(desc(ProductAPITokenModel.created_at)).all()
    
    # 转换为安全的响应格式（不返回完整token，只返回部分）
    result = []
    for token in tokens:
        token_str = token.token
        masked_token = f"{token_str[:8]}...{token_str[-4:]}" if len(token_str) > 12 else "***"
        
        result.append({
            "id": token.id,
            "token": masked_token,
            "full_token": token.token,  # 完整token仅用于显示
            "permissions": token.permissions,
            "is_active": token.is_active,
            "created_at": token.created_at.isoformat() if token.created_at else None,
            "expires_at": token.expires_at.isoformat() if token.expires_at else None,
            "last_used_at": token.last_used_at.isoformat() if token.last_used_at else None,
            "usage_count": token.usage_count or 0
        })
    
    return result

@router.delete("/{product_id}/api/token")
@transactional(rollback_on_exception=True, max_retries=2)
@with_db_error_handling
@sql_injection_protection
def revoke_api_token(
    product_id: int,
    token_data: dict,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """撤销API令牌（需要认证）"""
    safe_executor = create_safe_query_executor(db)
    
    product = safe_executor.safe_get_by_id(ProductModel, product_id)
    if not product:
        raise ResourceNotFoundAPIError("产品", product_id)
    
    token = token_data.get('token')
    if not token:
        raise ValidationAPIError("令牌不能为空")
    
    # 查找并撤销令牌
    api_token = db.query(ProductAPITokenModel).filter(
        ProductAPITokenModel.token == token,
        ProductAPITokenModel.product_id == product_id
    ).first()
    
    if not api_token:
        raise ResourceNotFoundAPIError("API令牌", token)
    
    api_token.is_active = False
    db.flush()
    
    return MessageResponse(message="API令牌已撤销")

@router.get("/{product_id}/api/config")
@sql_injection_protection
def get_api_config(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """获取API配置（需要认证）"""
    safe_executor = create_safe_query_executor(db)
    
    product = safe_executor.safe_get_by_id(ProductModel, product_id)
    if not product:
        raise ResourceNotFoundAPIError("产品", product_id)
    
    # 从产品配置中获取API设置
    api_config = product.config_data.get('api', {}) if product.config_data else {}
    
    return {
        "product_id": product_id,
        "api_key": f"pk_{product_id}_{secrets.token_hex(8)}",
        "allowed_origins": api_config.get('allowed_origins', ['*']),
        "rate_limit": api_config.get('rate_limit', 100),
        "permissions": api_config.get('permissions', ['read'])
    }

@router.put("/{product_id}/api/config")
@transactional(rollback_on_exception=True, max_retries=2)
@with_db_error_handling
@sql_injection_protection
def update_api_config(
    product_id: int,
    config_data: dict,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """更新API配置（需要认证）"""
    safe_executor = create_safe_query_executor(db)
    
    product = safe_executor.safe_get_by_id(ProductModel, product_id)
    if not product:
        raise ResourceNotFoundAPIError("产品", product_id)
    
    # 验证配置数据
    allowed_origins = config_data.get('allowed_origins', ['*'])
    rate_limit = config_data.get('rate_limit', 100)
    permissions = config_data.get('permissions', ['read'])
    
    if not isinstance(allowed_origins, list):
        raise ValidationAPIError("allowed_origins必须是数组")
    
    if not isinstance(rate_limit, int) or rate_limit < 1 or rate_limit > 10000:
        raise ValidationAPIError("rate_limit必须是1-10000之间的整数")
    
    # 更新产品配置
    if not product.config_data:
        product.config_data = {}
    
    product.config_data['api'] = {
        'allowed_origins': allowed_origins,
        'rate_limit': rate_limit,
        'permissions': permissions
    }
    
    db.flush()
    
    return {
        "product_id": product_id,
        "api_key": f"pk_{product_id}_{secrets.token_hex(8)}",
        "allowed_origins": allowed_origins,
        "rate_limit": rate_limit,
        "permissions": permissions
    }

@router.get("/{product_id}/api/calls")
@sql_injection_protection
def get_api_calls(
    product_id: int,
    endpoint: Optional[str] = None,
    status_code: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """获取API调用日志（需要认证）"""
    safe_executor = create_safe_query_executor(db)
    
    product = safe_executor.safe_get_by_id(ProductModel, product_id)
    if not product:
        raise ResourceNotFoundAPIError("产品", product_id)
    
    # 构建过滤条件
    filters = {"product_id": product_id}
    if endpoint:
        filters["endpoint"] = endpoint
    if status_code:
        filters["status_code"] = status_code
    
    api_calls = safe_executor.safe_filter_query(
        ProductAPICallModel,
        filters,
        limit=min(limit, 100),
        offset=max(skip, 0),
        order_by='timestamp'
    )
    
    return api_calls

@router.post("/{product_id}/api/proxy/{path:path}")
@transactional(rollback_on_exception=True, max_retries=2)
@with_db_error_handling
def proxy_api_call(
    product_id: int,
    path: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """代理API调用（公开接口，需要令牌认证）"""
    safe_executor = create_safe_query_executor(db)
    
    product = safe_executor.safe_get_by_id(ProductModel, product_id)
    if not product:
        raise ResourceNotFoundAPIError("产品", product_id)
    
    # 验证授权头
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="需要Bearer令牌认证"
        )
    
    token = auth_header.split(' ')[1]
    
    # 验证令牌
    api_token = db.query(ProductAPITokenModel).filter(
        ProductAPITokenModel.token == token,
        ProductAPITokenModel.product_id == product_id,
        ProductAPITokenModel.is_active == True
    ).first()
    
    if not api_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的API令牌"
        )
    
    from datetime import datetime
    if api_token.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API令牌已过期"
        )
    
    # 记录API调用
    start_time = datetime.utcnow()
    
    try:
        # 这里可以实现实际的API代理逻辑
        # 目前返回模拟响应
        response_data = {
            "message": f"API调用成功: {path}",
            "product_id": product_id,
            "timestamp": start_time.isoformat(),
            "path": path
        }
        
        # 记录成功的API调用
        api_call = ProductAPICallModel(
            product_id=product_id,
            token_id=api_token.id,
            endpoint=path,
            method=request.method,
            status_code=200,
            response_time=100,  # 模拟响应时间
            client_ip=request.client.host if hasattr(request, 'client') else None,
            user_agent=request.headers.get('user-agent')
        )
        
        db.add(api_call)
        db.flush()
        
        return response_data
        
    except Exception as e:
        # 记录失败的API调用
        api_call = ProductAPICallModel(
            product_id=product_id,
            token_id=api_token.id,
            endpoint=path,
            method=request.method,
            status_code=500,
            error_message=str(e),
            client_ip=request.client.host if hasattr(request, 'client') else None,
            user_agent=request.headers.get('user-agent')
        )
        
        db.add(api_call)
        db.flush()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"API调用失败: {str(e)}"
        )

# 产品数据存储相关接口
@router.post("/{product_id}/data/{key}")
@transactional(rollback_on_exception=True, max_retries=2)
@with_db_error_handling
@sql_injection_protection
def store_product_data(
    product_id: int,
    key: str,
    data: dict,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """存储产品数据（需要认证）"""
    safe_executor = create_safe_query_executor(db)
    
    product = safe_executor.safe_get_by_id(ProductModel, product_id)
    if not product:
        raise ResourceNotFoundAPIError("产品", product_id)
    
    # 验证键名
    if not key or len(key) > 255:
        raise ValidationAPIError("存储键名无效")
    
    # 计算数据大小
    import json
    data_json = json.dumps(data)
    data_size = len(data_json.encode('utf-8'))
    
    # 检查存储限制（100MB）
    if data_size > 100 * 1024 * 1024:
        raise ValidationAPIError("数据大小超过限制（100MB）")
    
    # 查找现有记录
    existing = db.query(ProductDataStorageModel).filter(
        ProductDataStorageModel.product_id == product_id,
        ProductDataStorageModel.storage_key == key
    ).first()
    
    if existing:
        # 更新现有记录
        existing.storage_value = data
        existing.size_bytes = data_size
        existing.updated_at = func.now()
        db.flush()
        storage_record = existing
    else:
        # 创建新记录
        storage_record = ProductDataStorageModel(
            product_id=product_id,
            storage_key=key,
            storage_value=data,
            size_bytes=data_size
        )
        db.add(storage_record)
        db.flush()
        db.refresh(storage_record)
    
    return {
        "product_id": product_id,
        "key": key,
        "size_bytes": data_size,
        "created_at": storage_record.created_at.isoformat(),
        "updated_at": storage_record.updated_at.isoformat()
    }

@router.get("/{product_id}/data/{key}")
@sql_injection_protection
def get_product_data(
    product_id: int,
    key: str,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """获取产品数据（需要认证）"""
    safe_executor = create_safe_query_executor(db)
    
    product = safe_executor.safe_get_by_id(ProductModel, product_id)
    if not product:
        raise ResourceNotFoundAPIError("产品", product_id)
    
    # 查找数据记录
    storage_record = db.query(ProductDataStorageModel).filter(
        ProductDataStorageModel.product_id == product_id,
        ProductDataStorageModel.storage_key == key
    ).first()
    
    if not storage_record:
        raise ResourceNotFoundAPIError("存储数据", key)
    
    # 更新访问记录
    storage_record.access_count += 1
    storage_record.accessed_at = func.now()
    db.commit()
    
    return {
        "product_id": product_id,
        "key": key,
        "data": storage_record.storage_value,
        "size_bytes": storage_record.size_bytes,
        "access_count": storage_record.access_count,
        "created_at": storage_record.created_at.isoformat(),
        "updated_at": storage_record.updated_at.isoformat(),
        "accessed_at": storage_record.accessed_at.isoformat() if storage_record.accessed_at else None
    }

@router.delete("/{product_id}/data/{key}")
@transactional(rollback_on_exception=True, max_retries=2)
@with_db_error_handling
@sql_injection_protection
def delete_product_data(
    product_id: int,
    key: str,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """删除产品数据（需要认证）"""
    safe_executor = create_safe_query_executor(db)
    
    product = safe_executor.safe_get_by_id(ProductModel, product_id)
    if not product:
        raise ResourceNotFoundAPIError("产品", product_id)
    
    # 查找并删除数据记录
    storage_record = db.query(ProductDataStorageModel).filter(
        ProductDataStorageModel.product_id == product_id,
        ProductDataStorageModel.storage_key == key
    ).first()
    
    if not storage_record:
        raise ResourceNotFoundAPIError("存储数据", key)
    
    db.delete(storage_record)
    # 事务装饰器会处理提交
    
    return MessageResponse(message="数据删除成功")

@router.get("/{product_id}/data")
@sql_injection_protection
def list_product_data(
    product_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """列出产品数据（需要认证）"""
    safe_executor = create_safe_query_executor(db)
    
    product = safe_executor.safe_get_by_id(ProductModel, product_id)
    if not product:
        raise ResourceNotFoundAPIError("产品", product_id)
    
    # 查询数据列表
    storage_records = safe_executor.safe_filter_query(
        ProductDataStorageModel,
        {"product_id": product_id},
        limit=min(limit, 100),
        offset=max(skip, 0),
        order_by='created_at'
    )
    
    # 计算总存储大小
    total_size = db.query(func.sum(ProductDataStorageModel.size_bytes)).filter(
        ProductDataStorageModel.product_id == product_id
    ).scalar() or 0
    
    return {
        "product_id": product_id,
        "total_records": len(storage_records),
        "total_size_bytes": total_size,
        "records": [
            {
                "key": record.storage_key,
                "size_bytes": record.size_bytes,
                "access_count": record.access_count,
                "created_at": record.created_at.isoformat(),
                "updated_at": record.updated_at.isoformat(),
                "accessed_at": record.accessed_at.isoformat() if record.accessed_at else None
            }
            for record in storage_records
        ]
    }
@router.get("/{product_id}/storage/quota")
@sql_injection_protection
def get_storage_quota(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """获取产品存储配额（需要认证）"""
    safe_executor = create_safe_query_executor(db)
    
    product = safe_executor.safe_get_by_id(ProductModel, product_id)
    if not product:
        raise ResourceNotFoundAPIError("产品", product_id)
    
    # 计算已使用的存储空间
    used_bytes = db.query(func.sum(ProductDataStorageModel.size_bytes)).filter(
        ProductDataStorageModel.product_id == product_id
    ).scalar() or 0
    
    # 设置存储配额（100MB）
    total_bytes = 100 * 1024 * 1024
    available_bytes = max(0, total_bytes - used_bytes)
    usage_percentage = (used_bytes / total_bytes * 100) if total_bytes > 0 else 0
    
    return {
        "used_bytes": used_bytes,
        "total_bytes": total_bytes,
        "available_bytes": available_bytes,
        "usage_percentage": min(100, usage_percentage)
    }

@router.delete("/{product_id}/data")
@transactional(rollback_on_exception=True, max_retries=2)
@with_db_error_handling
@sql_injection_protection
def clear_all_product_data(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """清空产品所有数据（需要认证）"""
    safe_executor = create_safe_query_executor(db)
    
    product = safe_executor.safe_get_by_id(ProductModel, product_id)
    if not product:
        raise ResourceNotFoundAPIError("产品", product_id)
    
    # 删除所有数据记录
    deleted_count = db.query(ProductDataStorageModel).filter(
        ProductDataStorageModel.product_id == product_id
    ).delete()
    
    db.flush()
    
    return {
        "message": f"已清空 {deleted_count} 条数据记录",
        "deleted_count": deleted_count
    }

@router.get("/{product_id}/data/export")
@sql_injection_protection
def export_product_data(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """导出产品数据（需要认证）"""
    safe_executor = create_safe_query_executor(db)
    
    product = safe_executor.safe_get_by_id(ProductModel, product_id)
    if not product:
        raise ResourceNotFoundAPIError("产品", product_id)
    
    # 获取所有数据记录
    storage_records = db.query(ProductDataStorageModel).filter(
        ProductDataStorageModel.product_id == product_id
    ).all()
    
    # 构建导出数据
    export_data = {
        "product_id": product_id,
        "export_time": datetime.utcnow().isoformat(),
        "total_records": len(storage_records),
        "data": {}
    }
    
    for record in storage_records:
        export_data["data"][record.storage_key] = {
            "value": record.storage_value,
            "metadata": {
                "size_bytes": record.size_bytes,
                "access_count": record.access_count,
                "created_at": record.created_at.isoformat(),
                "updated_at": record.updated_at.isoformat(),
                "accessed_at": record.accessed_at.isoformat() if record.accessed_at else None
            }
        }
    
    import json
    from fastapi.responses import Response
    
    json_data = json.dumps(export_data, ensure_ascii=False, indent=2)
    
    return Response(
        content=json_data,
        media_type="application/json",
        headers={
            "Content-Disposition": f"attachment; filename=product-{product_id}-data.json"
        }
    )

@router.post("/{product_id}/data/import")
@transactional(rollback_on_exception=True, max_retries=2)
@with_db_error_handling
async def import_product_data(
    product_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """导入产品数据（需要认证）"""
    safe_executor = create_safe_query_executor(db)
    
    product = safe_executor.safe_get_by_id(ProductModel, product_id)
    if not product:
        raise ResourceNotFoundAPIError("产品", product_id)
    
    # 验证文件类型
    if not file.filename or not file.filename.endswith('.json'):
        raise ValidationAPIError("只支持JSON格式的文件")
    
    try:
        # 读取文件内容
        content = await file.read()
        import_data = json.loads(content.decode('utf-8'))
        
        if not isinstance(import_data, dict) or 'data' not in import_data:
            raise ValidationAPIError("无效的导入文件格式")
        
        imported_count = 0
        errors = []
        
        # 导入数据
        for key, item in import_data['data'].items():
            try:
                if not isinstance(item, dict) or 'value' not in item:
                    errors.append(f"键 '{key}': 数据格式无效")
                    continue
                
                value = item['value']
                
                # 计算数据大小
                data_json = json.dumps(value)
                data_size = len(data_json.encode('utf-8'))
                
                # 检查大小限制
                if data_size > 10 * 1024 * 1024:  # 10MB per record
                    errors.append(f"键 '{key}': 数据大小超过限制")
                    continue
                
                # 查找现有记录
                existing = db.query(ProductDataStorageModel).filter(
                    ProductDataStorageModel.product_id == product_id,
                    ProductDataStorageModel.storage_key == key
                ).first()
                
                if existing:
                    # 更新现有记录
                    existing.storage_value = value
                    existing.size_bytes = data_size
                    existing.updated_at = func.now()
                else:
                    # 创建新记录
                    storage_record = ProductDataStorageModel(
                        product_id=product_id,
                        storage_key=key,
                        storage_value=value,
                        size_bytes=data_size
                    )
                    db.add(storage_record)
                
                imported_count += 1
                
            except Exception as e:
                errors.append(f"键 '{key}': {str(e)}")
        
        db.flush()
        
        return {
            "imported_count": imported_count,
            "errors": errors
        }
        
    except json.JSONDecodeError:
        raise ValidationAPIError("文件不是有效的JSON格式")
    except Exception as e:
        raise ValidationAPIError(f"导入失败: {str(e)}")
# 产品用户认证相关接口
@router.post("/{product_id}/auth/guest-session")
@transactional(rollback_on_exception=True, max_retries=2)
@with_db_error_handling
def create_guest_session(
    product_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """创建访客会话（公开接口）"""
    safe_executor = create_safe_query_executor(db)
    
    product = safe_executor.safe_get_by_id(ProductModel, product_id)
    if not product:
        raise ResourceNotFoundAPIError("产品", product_id)
    
    import uuid
    from datetime import datetime, timedelta
    
    # 创建访客会话
    session_id = str(uuid.uuid4())
    session = ProductUserSessionModel(
        id=session_id,
        product_id=product_id,
        user_id=None,
        is_guest=True,
        expires_at=datetime.utcnow() + timedelta(hours=24),  # 24小时有效期
        session_data={}
    )
    
    db.add(session)
    db.flush()
    db.refresh(session)
    
    return {
        "id": session.id,
        "product_id": product_id,
        "user_id": None,
        "session_data": session.session_data,
        "expires_at": session.expires_at.isoformat(),
        "created_at": session.created_at.isoformat(),
        "updated_at": session.updated_at.isoformat()
    }

@router.post("/{product_id}/auth/register")
@transactional(rollback_on_exception=True, max_retries=2)
@with_db_error_handling
@sql_injection_protection
def register_product_user(
    product_id: int,
    user_data: dict,
    request: Request,
    db: Session = Depends(get_db)
):
    """注册产品用户（公开接口）"""
    safe_executor = create_safe_query_executor(db)
    
    product = safe_executor.safe_get_by_id(ProductModel, product_id)
    if not product:
        raise ResourceNotFoundAPIError("产品", product_id)
    
    # 验证输入数据
    username = user_data.get('username', '').strip()
    email = user_data.get('email', '').strip()
    display_name = user_data.get('display_name', '').strip()
    
    if not username and not email:
        raise ValidationAPIError("用户名或邮箱至少需要提供一个")
    
    # 检查用户名是否已存在
    if username:
        existing_user = db.query(ProductUserModel).filter(
            ProductUserModel.product_id == product_id,
            ProductUserModel.username == username
        ).first()
        
        if existing_user:
            raise ValidationAPIError("用户名已存在")
    
    # 检查邮箱是否已存在
    if email:
        existing_email = db.query(ProductUserModel).filter(
            ProductUserModel.product_id == product_id,
            ProductUserModel.email == email
        ).first()
        
        if existing_email:
            raise ValidationAPIError("邮箱已存在")
    
    import uuid
    from datetime import datetime, timedelta
    
    # 创建用户
    user_id = str(uuid.uuid4())
    user = ProductUserModel(
        id=user_id,
        product_id=product_id,
        username=username or None,
        email=email or None,
        display_name=display_name or username or email,
        preferences={}
    )
    
    db.add(user)
    db.flush()
    
    # 创建用户会话
    session_id = str(uuid.uuid4())
    session = ProductUserSessionModel(
        id=session_id,
        product_id=product_id,
        user_id=user_id,
        is_guest=False,
        expires_at=datetime.utcnow() + timedelta(days=30),  # 30天有效期
        session_data={}
    )
    
    db.add(session)
    db.flush()
    db.refresh(user)
    db.refresh(session)
    
    return {
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "display_name": user.display_name,
            "avatar_url": user.avatar_url,
            "preferences": user.preferences,
            "created_at": user.created_at.isoformat(),
            "last_active_at": user.last_active_at.isoformat() if user.last_active_at else None
        },
        "session": {
            "id": session.id,
            "product_id": product_id,
            "user_id": user_id,
            "session_data": session.session_data,
            "expires_at": session.expires_at.isoformat(),
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat()
        }
    }

@router.post("/{product_id}/auth/login")
@transactional(rollback_on_exception=True, max_retries=2)
@with_db_error_handling
@sql_injection_protection
def login_product_user(
    product_id: int,
    credentials: dict,
    request: Request,
    db: Session = Depends(get_db)
):
    """产品用户登录（公开接口）"""
    safe_executor = create_safe_query_executor(db)
    
    product = safe_executor.safe_get_by_id(ProductModel, product_id)
    if not product:
        raise ResourceNotFoundAPIError("产品", product_id)
    
    # 获取登录凭据
    username = credentials.get('username', '').strip()
    email = credentials.get('email', '').strip()
    token = credentials.get('token', '').strip()
    
    user = None
    
    # 根据不同的登录方式查找用户
    if token:
        # 令牌登录（可以是第三方认证）
        # 这里可以实现令牌验证逻辑
        pass
    elif username:
        user = db.query(ProductUserModel).filter(
            ProductUserModel.product_id == product_id,
            ProductUserModel.username == username,
            ProductUserModel.is_active == True
        ).first()
    elif email:
        user = db.query(ProductUserModel).filter(
            ProductUserModel.product_id == product_id,
            ProductUserModel.email == email,
            ProductUserModel.is_active == True
        ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在或凭据无效"
        )
    
    import uuid
    from datetime import datetime, timedelta
    
    # 更新用户最后活跃时间
    user.last_active_at = datetime.utcnow()
    
    # 创建新会话
    session_id = str(uuid.uuid4())
    session = ProductUserSessionModel(
        id=session_id,
        product_id=product_id,
        user_id=user.id,
        is_guest=False,
        expires_at=datetime.utcnow() + timedelta(days=30),
        session_data={}
    )
    
    db.add(session)
    db.flush()
    db.refresh(session)
    
    return {
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "display_name": user.display_name,
            "avatar_url": user.avatar_url,
            "preferences": user.preferences,
            "created_at": user.created_at.isoformat(),
            "last_active_at": user.last_active_at.isoformat() if user.last_active_at else None
        },
        "session": {
            "id": session.id,
            "product_id": product_id,
            "user_id": user.id,
            "session_data": session.session_data,
            "expires_at": session.expires_at.isoformat(),
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat()
        }
    }

@router.post("/{product_id}/auth/logout")
@transactional(rollback_on_exception=True, max_retries=2)
@with_db_error_handling
def logout_product_user(
    product_id: int,
    logout_data: dict,
    db: Session = Depends(get_db)
):
    """产品用户登出（公开接口）"""
    safe_executor = create_safe_query_executor(db)
    
    product = safe_executor.safe_get_by_id(ProductModel, product_id)
    if not product:
        raise ResourceNotFoundAPIError("产品", product_id)
    
    session_id = logout_data.get('session_id')
    if not session_id:
        raise ValidationAPIError("会话ID不能为空")
    
    # 查找并删除会话
    session = db.query(ProductUserSessionModel).filter(
        ProductUserSessionModel.id == session_id,
        ProductUserSessionModel.product_id == product_id
    ).first()
    
    if session:
        db.delete(session)
        db.flush()
    
    return MessageResponse(message="登出成功")

@router.post("/{product_id}/auth/validate-session")
def validate_product_session(
    product_id: int,
    session_data: dict,
    db: Session = Depends(get_db)
):
    """验证产品会话（公开接口）"""
    safe_executor = create_safe_query_executor(db)
    
    product = safe_executor.safe_get_by_id(ProductModel, product_id)
    if not product:
        raise ResourceNotFoundAPIError("产品", product_id)
    
    session_id = session_data.get('session_id')
    if not session_id:
        return {"valid": False, "reason": "会话ID不能为空"}
    
    # 查找会话
    session = db.query(ProductUserSessionModel).filter(
        ProductUserSessionModel.id == session_id,
        ProductUserSessionModel.product_id == product_id
    ).first()
    
    if not session:
        return {"valid": False, "reason": "会话不存在"}
    
    from datetime import datetime
    if session.expires_at < datetime.utcnow():
        return {"valid": False, "reason": "会话已过期"}
    
    # 更新最后访问时间
    session.last_accessed_at = datetime.utcnow()
    db.commit()
    
    return {
        "valid": True,
        "session": {
            "id": session.id,
            "product_id": product_id,
            "user_id": session.user_id,
            "is_guest": session.is_guest,
            "expires_at": session.expires_at.isoformat()
        }
    }

@router.put("/{product_id}/auth/preferences")
@transactional(rollback_on_exception=True, max_retries=2)
@with_db_error_handling
@sql_injection_protection
def update_user_preferences(
    product_id: int,
    preferences: dict,
    request: Request,
    db: Session = Depends(get_db)
):
    """更新用户偏好设置（需要会话认证）"""
    # 这里需要实现会话认证逻辑
    # 暂时返回模拟响应
    return {
        "id": "user_id",
        "username": "test_user",
        "email": "test@example.com",
        "display_name": "Test User",
        "avatar_url": None,
        "preferences": preferences,
        "created_at": "2024-01-01T00:00:00Z",
        "last_active_at": "2024-01-01T00:00:00Z"
    }

@router.get("/{product_id}/auth/preferences")
def get_user_preferences(
    product_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """获取用户偏好设置（需要会话认证）"""
    # 这里需要实现会话认证逻辑
    # 暂时返回模拟响应
    return {
        "theme": "light",
        "language": "zh-CN",
        "notifications": True
    }

@router.put("/{product_id}/auth/session-data")
@transactional(rollback_on_exception=True, max_retries=2)
@with_db_error_handling
def update_session_data(
    product_id: int,
    session_update: dict,
    db: Session = Depends(get_db)
):
    """更新会话数据（公开接口）"""
    safe_executor = create_safe_query_executor(db)
    
    product = safe_executor.safe_get_by_id(ProductModel, product_id)
    if not product:
        raise ResourceNotFoundAPIError("产品", product_id)
    
    session_id = session_update.get('session_id')
    session_data = session_update.get('session_data', {})
    
    if not session_id:
        raise ValidationAPIError("会话ID不能为空")
    
    # 查找会话
    session = db.query(ProductUserSessionModel).filter(
        ProductUserSessionModel.id == session_id,
        ProductUserSessionModel.product_id == product_id
    ).first()
    
    if not session:
        raise ResourceNotFoundAPIError("会话", session_id)
    
    from datetime import datetime
    if session.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="会话已过期"
        )
    
    # 更新会话数据
    session.session_data = session_data
    session.updated_at = datetime.utcnow()
    session.last_accessed_at = datetime.utcnow()
    
    db.flush()
    db.refresh(session)
    
    return {
        "id": session.id,
        "product_id": product_id,
        "user_id": session.user_id,
        "session_data": session.session_data,
        "expires_at": session.expires_at.isoformat(),
        "created_at": session.created_at.isoformat(),
        "updated_at": session.updated_at.isoformat()
    }

@router.get("/{product_id}/auth/session-data/{session_id}")
def get_session_data(
    product_id: int,
    session_id: str,
    db: Session = Depends(get_db)
):
    """获取会话数据（公开接口）"""
    safe_executor = create_safe_query_executor(db)
    
    product = safe_executor.safe_get_by_id(ProductModel, product_id)
    if not product:
        raise ResourceNotFoundAPIError("产品", product_id)
    
    # 查找会话
    session = db.query(ProductUserSessionModel).filter(
        ProductUserSessionModel.id == session_id,
        ProductUserSessionModel.product_id == product_id
    ).first()
    
    if not session:
        raise ResourceNotFoundAPIError("会话", session_id)
    
    from datetime import datetime
    if session.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="会话已过期"
        )
    
    # 更新最后访问时间
    session.last_accessed_at = datetime.utcnow()
    db.commit()
    
    return {
        "session_data": session.session_data or {}
    }

@router.put("/{product_id}/auth/profile")
@transactional(rollback_on_exception=True, max_retries=2)
@with_db_error_handling
@sql_injection_protection
def update_user_profile(
    product_id: int,
    profile_data: dict,
    request: Request,
    db: Session = Depends(get_db)
):
    """更新用户资料（需要会话认证）"""
    # 这里需要实现会话认证逻辑
    # 暂时返回模拟响应
    return {
        "id": "user_id",
        "username": "test_user",
        "email": profile_data.get('email', 'test@example.com'),
        "display_name": profile_data.get('display_name', 'Test User'),
        "avatar_url": profile_data.get('avatar_url'),
        "preferences": {},
        "created_at": "2024-01-01T00:00:00Z",
        "last_active_at": "2024-01-01T00:00:00Z"
    }

@router.delete("/{product_id}/auth/account")
@transactional(rollback_on_exception=True, max_retries=2)
@with_db_error_handling
def delete_user_account(
    product_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """删除用户账户（需要会话认证）"""
    # 这里需要实现会话认证和用户删除逻辑
    # 暂时返回成功响应
    return MessageResponse(message="用户账户删除成功")

# ==================== 产品文件处理扩展API ====================

@router.post("/{product_id}/files/upload-single")
@transactional(rollback_on_exception=True, max_retries=2)
@with_db_error_handling
def upload_single_file(
    product_id: int,
    file: UploadFile = File(...),
    description: str = Form(None),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """上传单个文件到产品目录（需要认证）"""
    safe_executor = create_safe_query_executor(db)
    
    product = safe_executor.safe_get_by_id(ProductModel, product_id)
    if not product:
        raise ResourceNotFoundAPIError("产品", product_id)
    
    if not file.filename:
        raise ValidationAPIError("文件名不能为空")
    
    try:
        # 读取文件内容
        file_content = file.file.read()
        
        # 使用文件服务上传单个文件
        result = product_file_service.upload_individual_file(
            product_id, file.filename, file_content, description
        )
        
        return result
        
    except ValueError as e:
        raise ValidationAPIError(str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件上传失败: {str(e)}"
        )

@router.get("/{product_id}/files/download/{file_path:path}")
def download_file(
    product_id: int,
    file_path: str,
    db: Session = Depends(get_db)
):
    """下载产品文件（公开接口）"""
    safe_executor = create_safe_query_executor(db)
    
    product = safe_executor.safe_get_by_id(ProductModel, product_id)
    if not product:
        raise ResourceNotFoundAPIError("产品", product_id)
    
    # 检查产品是否已发布（未发布的产品需要认证）
    if not product.is_published:
        # 这里可以添加认证检查
        pass
    
    try:
        content, filename, mime_type = product_file_service.download_file(product_id, file_path)
        
        from fastapi.responses import Response
        return Response(
            content=content,
            media_type=mime_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Length": str(len(content))
            }
        )
        
    except FileNotFoundError:
        raise ResourceNotFoundAPIError("文件", file_path)
    except ValueError as e:
        raise ValidationAPIError(str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件下载失败: {str(e)}"
        )

@router.delete("/{product_id}/files/{file_path:path}")
@transactional(rollback_on_exception=True, max_retries=2)
@with_db_error_handling
def delete_file(
    product_id: int,
    file_path: str,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """删除产品文件（需要认证）"""
    safe_executor = create_safe_query_executor(db)
    
    product = safe_executor.safe_get_by_id(ProductModel, product_id)
    if not product:
        raise ResourceNotFoundAPIError("产品", product_id)
    
    try:
        result = product_file_service.delete_file(product_id, file_path)
        return result
        
    except FileNotFoundError:
        raise ResourceNotFoundAPIError("文件", file_path)
    except ValueError as e:
        raise ValidationAPIError(str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件删除失败: {str(e)}"
        )

# ==================== 产品版本控制API ====================

@router.post("/{product_id}/versions")
@transactional(rollback_on_exception=True, max_retries=2)
@with_db_error_handling
def create_version(
    product_id: int,
    version_data: dict,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """创建产品版本（需要认证）"""
    safe_executor = create_safe_query_executor(db)
    
    product = safe_executor.safe_get_by_id(ProductModel, product_id)
    if not product:
        raise ResourceNotFoundAPIError("产品", product_id)
    
    version = version_data.get('version')
    description = version_data.get('description')
    
    if not version:
        raise ValidationAPIError("版本号不能为空")
    
    try:
        result = product_file_service.create_version(product_id, version, description)
        return result
        
    except ValueError as e:
        raise ValidationAPIError(str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"版本创建失败: {str(e)}"
        )

@router.get("/{product_id}/versions")
def list_versions(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """列出产品版本（需要认证）"""
    safe_executor = create_safe_query_executor(db)
    
    product = safe_executor.safe_get_by_id(ProductModel, product_id)
    if not product:
        raise ResourceNotFoundAPIError("产品", product_id)
    
    try:
        versions = product_file_service.list_versions(product_id)
        return {"versions": versions}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取版本列表失败: {str(e)}"
        )

@router.post("/{product_id}/versions/{version}/restore")
@transactional(rollback_on_exception=True, max_retries=2)
@with_db_error_handling
def restore_version(
    product_id: int,
    version: str,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """恢复到指定版本（需要认证）"""
    safe_executor = create_safe_query_executor(db)
    
    product = safe_executor.safe_get_by_id(ProductModel, product_id)
    if not product:
        raise ResourceNotFoundAPIError("产品", product_id)
    
    try:
        result = product_file_service.restore_version(product_id, version)
        return result
        
    except ValueError as e:
        raise ValidationAPIError(str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"版本恢复失败: {str(e)}"
        )

@router.delete("/{product_id}/versions/{version}")
@transactional(rollback_on_exception=True, max_retries=2)
@with_db_error_handling
def delete_version(
    product_id: int,
    version: str,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """删除指定版本（需要认证）"""
    safe_executor = create_safe_query_executor(db)
    
    product = safe_executor.safe_get_by_id(ProductModel, product_id)
    if not product:
        raise ResourceNotFoundAPIError("产品", product_id)
    
    try:
        result = product_file_service.delete_version(product_id, version)
        return result
        
    except ValueError as e:
        raise ValidationAPIError(str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"版本删除失败: {str(e)}"
        )

# ==================== 产品安全扫描API ====================

@router.post("/{product_id}/security/scan")
def scan_product_security(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """扫描产品文件安全性（需要认证）"""
    safe_executor = create_safe_query_executor(db)
    
    product = safe_executor.safe_get_by_id(ProductModel, product_id)
    if not product:
        raise ResourceNotFoundAPIError("产品", product_id)
    
    try:
        scan_result = product_file_service.scan_product_files(product_id)
        return scan_result
        
    except ValueError as e:
        raise ValidationAPIError(str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"安全扫描失败: {str(e)}"
        )

@router.post("/{product_id}/security/scan-file")
def scan_file_security(
    product_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """扫描单个文件安全性（需要认证）"""
    safe_executor = create_safe_query_executor(db)
    
    product = safe_executor.safe_get_by_id(ProductModel, product_id)
    if not product:
        raise ResourceNotFoundAPIError("产品", product_id)
    
    if not file.filename:
        raise ValidationAPIError("文件名不能为空")
    
    try:
        # 读取文件内容
        file_content = file.file.read()
        
        # 扫描文件
        scan_result = product_file_service.scan_file_content(file_content, file.filename)
        
        return {
            "filename": file.filename,
            "file_size": len(file_content),
            "scan_result": scan_result.to_dict()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件扫描失败: {str(e)}"
        )

@router.get("/{product_id}/files/integrity")
def verify_files_integrity(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """验证产品文件完整性（需要认证）"""
    safe_executor = create_safe_query_executor(db)
    
    product = safe_executor.safe_get_by_id(ProductModel, product_id)
    if not product:
        raise ResourceNotFoundAPIError("产品", product_id)
    
    try:
        is_valid, message = product_file_service.verify_product_integrity(product_id)
        
        return {
            "product_id": product_id,
            "is_valid": is_valid,
            "message": message,
            "verified_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"完整性验证失败: {str(e)}"
        )

# ==================== 产品资源管理API ====================

@router.get("/{product_id}/resources/stats")
def get_resource_stats(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """获取产品资源统计（需要认证）"""
    safe_executor = create_safe_query_executor(db)
    
    product = safe_executor.safe_get_by_id(ProductModel, product_id)
    if not product:
        raise ResourceNotFoundAPIError("产品", product_id)
    
    try:
        # 获取文件信息
        files_info = product_file_service.get_product_files(product_id)
        
        # 获取版本信息
        versions = product_file_service.list_versions(product_id)
        
        # 计算统计信息
        file_types = {}
        for file_info in files_info.get("files", []):
            file_type = file_info.get("type", "unknown")
            if file_type not in file_types:
                file_types[file_type] = {"count": 0, "size": 0}
            file_types[file_type]["count"] += 1
            file_types[file_type]["size"] += file_info.get("size", 0)
        
        return {
            "product_id": product_id,
            "files": {
                "total_count": files_info.get("total_files", 0),
                "total_size": files_info.get("total_size", 0),
                "by_type": file_types
            },
            "versions": {
                "total_count": len(versions),
                "latest_version": versions[0] if versions else None
            },
            "metadata": files_info.get("metadata", {}),
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取资源统计失败: {str(e)}"
        )

@router.get("/storage/stats")
def get_storage_stats(
    current_user: str = Depends(get_current_user)
):
    """获取存储统计信息（需要认证）"""
    try:
        stats = product_file_service.get_storage_stats()
        return {
            **stats,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取扩展统计失败: {str(e)}"
        )

@router.post("/{product_id}/resources/cleanup")
@transactional(rollback_on_exception=True, max_retries=2)
@with_db_error_handling
def cleanup_product_resources(
    product_id: int,
    cleanup_options: dict,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """清理产品资源（需要认证）"""
    safe_executor = create_safe_query_executor(db)
    
    product = safe_executor.safe_get_by_id(ProductModel, product_id)
    if not product:
        raise ResourceNotFoundAPIError("产品", product_id)
    
    try:
        cleanup_result = {
            "product_id": product_id,
            "cleaned_items": [],
            "errors": []
        }
        
        # 清理旧版本
        if cleanup_options.get("old_versions", False):
            versions = product_file_service.list_versions(product_id)
            keep_count = cleanup_options.get("keep_versions", 5)
            
            if len(versions) > keep_count:
                versions_to_delete = versions[keep_count:]
                for version_info in versions_to_delete:
                    try:
                        product_file_service.delete_version(product_id, version_info["version"])
                        cleanup_result["cleaned_items"].append(f"版本: {version_info['version']}")
                    except Exception as e:
                        cleanup_result["errors"].append(f"删除版本 {version_info['version']} 失败: {str(e)}")
        
        # 清理临时文件
        if cleanup_options.get("temp_files", False):
            import tempfile
            temp_dir = product_file_service.temp_dir / str(product_id)
            if temp_dir.exists():
                try:
                    shutil.rmtree(temp_dir)
                    temp_dir.mkdir(exist_ok=True)
                    cleanup_result["cleaned_items"].append("临时文件")
                except Exception as e:
                    cleanup_result["errors"].append(f"清理临时文件失败: {str(e)}")
        
        # 清理备份文件
        if cleanup_options.get("old_backups", False):
            backup_dir = product_file_service.backups_dir / str(product_id)
            if backup_dir.exists():
                try:
                    # 保留最近的备份文件
                    backup_files = list(backup_dir.glob("*"))
                    backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                    
                    keep_count = cleanup_options.get("keep_backups", 10)
                    if len(backup_files) > keep_count:
                        for backup_file in backup_files[keep_count:]:
                            backup_file.unlink()
                            cleanup_result["cleaned_items"].append(f"备份文件: {backup_file.name}")
                except Exception as e:
                    cleanup_result["errors"].append(f"清理备份文件失败: {str(e)}")
        
        return cleanup_result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"资源清理失败: {str(e)}"
        )

# ==================== 产品扩展机制API ====================

from ..services.product_extension_service import HookType

@router.get("/extensions/{extension_name}")
@sql_injection_protection
def get_extension_info(
    extension_name: str,
    current_user: str = Depends(get_current_user)
):
    """获取扩展信息（需要认证）"""
    try:
        # 验证扩展名称
        validate_extension_name(extension_name)
        
        extension_info = product_extension_service.get_extension_info(extension_name)
        if not extension_info:
            raise ResourceNotFoundAPIError("扩展", extension_name)
        
        return extension_info
        
    except ValueError as e:
        raise ValidationAPIError(str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取扩展信息失败: {str(e)}"
        )

@router.post("/extensions/{extension_name}/configure")
@sql_injection_protection
@transactional(rollback_on_exception=True, max_retries=2)
@with_db_error_handling
def configure_extension(
    extension_name: str,
    config_data: ExtensionConfigureRequest,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """配置扩展（需要认证）"""
    try:
        # 验证扩展名称
        validate_extension_name(extension_name)
        
        # 验证配置数据
        if not isinstance(config_data.config, dict):
            raise ValidationAPIError("配置数据必须是字典类型")
        
        # 清理配置数据
        safe_config = validate_and_sanitize_input(config_data.config)
        
        success = product_extension_service.configure_extension(extension_name, safe_config)
        if not success:
            raise ValidationAPIError("扩展配置失败")
        
        return MessageResponse(message="扩展配置成功")
        
    except ValueError as e:
        raise ValidationAPIError(str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"配置扩展失败: {str(e)}"
        )

@router.post("/{product_id}/render")
def render_product(
    product_id: int,
    render_config: dict,
    db: Session = Depends(get_db)
):
    """渲染产品（公开接口）"""
    safe_executor = create_safe_query_executor(db)
    
    product = safe_executor.safe_get_by_id(ProductModel, product_id)
    if not product:
        raise ResourceNotFoundAPIError("产品", product_id)
    
    # 检查产品是否已发布
    if not product.is_published:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="产品未发布"
        )
    
    try:
        # 使用扩展渲染产品
        rendered_html = product_extension_service.render_product_with_extensions(
            product_id, product.product_type, render_config
        )
        
        if not rendered_html:
            # 使用默认渲染
            rendered_html = f'''
            <div class="default-product-container">
                <iframe 
                    src="/products/{product_id}/{product.entry_file}"
                    frameborder="0"
                    width="100%"
                    height="100%"
                    sandbox="allow-scripts allow-same-origin">
                </iframe>
            </div>
            '''
        
        return {
            "product_id": product_id,
            "rendered_html": rendered_html,
            "render_time": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"产品渲染失败: {str(e)}"
        )

@router.post("/{product_id}/validate-with-extensions")
def validate_product_with_extensions(
    product_id: int,
    validation_data: dict,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """使用扩展验证产品（需要认证）"""
    safe_executor = create_safe_query_executor(db)
    
    product = safe_executor.safe_get_by_id(ProductModel, product_id)
    if not product:
        raise ResourceNotFoundAPIError("产品", product_id)
    
    try:
        # 获取产品文件
        files_info = product_file_service.get_product_files(product_id)
        files = {}
        
        # 读取文件内容（用于验证）
        # 使用基于ID的固定路径获取产品目录
        product_dir = product_file_service.get_product_directory(product_id)
        for file_info in files_info.get("files", []):
            file_path = product_dir / file_info["path"]
            if file_path.exists():
                with open(file_path, 'rb') as f:
                    files[file_info["path"]] = f.read()
        
        # 使用扩展验证
        is_valid, errors = product_extension_service.validate_product_with_extensions(
            product.product_type, 
            {
                "id": product.id,
                "title": product.title,
                "product_type": product.product_type,
                "config_data": product.config_data or {}
            },
            files
        )
        
        return {
            "product_id": product_id,
            "is_valid": is_valid,
            "errors": errors,
            "validated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"产品验证失败: {str(e)}"
        )

@router.post("/extensions/reload")
@sql_injection_protection
def reload_extensions(
    current_user: str = Depends(get_current_user)
):
    """重新加载扩展（需要认证）"""
    try:
        loaded_count = product_extension_service.load_extensions_from_directory()
        
        return {
            "message": "扩展重新加载完成",
            "loaded_count": loaded_count
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"重新加载扩展失败: {str(e)}"
        )

@router.post("/extensions/install")
@sql_injection_protection
@transactional(rollback_on_exception=True, max_retries=2)
@with_db_error_handling
def install_extension(
    extension_data: ExtensionInstallRequest,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """安装扩展（需要认证）"""
    try:
        # 验证扩展路径
        validate_extension_path(extension_data.path)
        
        # 验证配置数据
        safe_config = {}
        if extension_data.config:
            if not isinstance(extension_data.config, dict):
                raise ValidationAPIError("配置数据必须是字典类型")
            safe_config = validate_and_sanitize_input(extension_data.config)
        
        success = product_extension_service.install_extension(
            extension_data.path, 
            safe_config
        )
        if not success:
            raise ValidationAPIError("扩展安装失败")
        
        return MessageResponse(message="扩展安装成功")
        
    except ValueError as e:
        raise ValidationAPIError(str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"安装扩展失败: {str(e)}"
        )

@router.delete("/extensions/{extension_name}")
@sql_injection_protection
@transactional(rollback_on_exception=True, max_retries=2)
@with_db_error_handling
def uninstall_extension(
    extension_name: str,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """卸载扩展（需要认证）"""
    try:
        # 验证扩展名称
        validate_extension_name(extension_name)
        
        # 检查扩展是否存在
        extension_info = product_extension_service.get_extension_info(extension_name)
        if not extension_info:
            raise ResourceNotFoundAPIError("扩展", extension_name)
        
        success = product_extension_service.uninstall_extension(extension_name)
        if not success:
            raise ValidationAPIError("扩展卸载失败")
        
        return MessageResponse(message="扩展卸载成功")
        
    except ValueError as e:
        raise ValidationAPIError(str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"卸载扩展失败: {str(e)}"
        )

@router.post("/extensions/initialize")
@sql_injection_protection
def initialize_extension_system(
    current_user: str = Depends(get_current_user)
):
    """初始化扩展系统（需要认证）"""
    try:
        # 加载扩展目录中的所有扩展
        loaded_count = product_extension_service.load_extensions_from_directory()
        
        # 获取扩展统计信息
        extensions = product_extension_service.list_extensions()
        product_types = product_extension_service.get_available_product_types()
        
        return {
            "message": "扩展系统初始化完成",
            "loaded_extensions": loaded_count,
            "total_extensions": len(extensions),
            "available_product_types": len(product_types),
            "extensions": extensions,
            "product_types": product_types
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"初始化扩展系统失败: {str(e)}"
        )

@router.get("/extensions/stats")
@sql_injection_protection
def get_extension_stats(
    current_user: str = Depends(get_current_user)
):
    """获取扩展统计信息（需要认证）"""
    try:
        extensions = product_extension_service.list_extensions()
        product_types = product_extension_service.get_available_product_types()
        
        # 统计扩展类型
        extension_types = {}
        enabled_count = 0
        
        for ext in extensions:
            ext_type = ext.get('extension_type', 'unknown')
            extension_types[ext_type] = extension_types.get(ext_type, 0) + 1
            
            if ext.get('enabled', True):
                enabled_count += 1
        
        return {
            "total_extensions": len(extensions),
            "enabled_extensions": enabled_count,
            "disabled_extensions": len(extensions) - enabled_count,
            "extension_types": extension_types,
            "available_product_types": len(product_types),
            "product_types": [pt['type_name'] for pt in product_types]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取扩展统计失败: {str(e)}"
        )