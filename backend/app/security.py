"""
SQL注入防护和安全查询模块

提供安全的数据库查询方法，防止SQL注入攻击
"""

import re
import logging
from typing import Any, Dict, List, Optional, Union
from sqlalchemy.orm import Session, Query
from sqlalchemy import text, and_, or_
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

class SQLInjectionError(Exception):
    """SQL注入攻击检测异常"""
    pass

class SecurityQueryBuilder:
    """安全查询构建器"""
    
    # SQL注入攻击模式
    INJECTION_PATTERNS = [
        r"(\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b)",
        r"(--|#|/\*|\*/)",
        r"(\b(or|and)\s+\d+\s*=\s*\d+)",
        r"(\b(or|and)\s+['\"].*['\"])",
        r"(;|\|\||&&)",
        r"(\bxp_cmdshell\b)",
        r"(\bsp_executesql\b)",
        r"(\binto\s+outfile\b)",
        r"(\bload_file\b)",
        r"(\bchar\s*\(\s*\d+\s*\))",
        r"(\bhex\s*\()",
        r"(\bconcat\s*\()",
        r"(\bsubstring\s*\()",
        r"(\bascii\s*\()",
        r"(\border\s+by\b)",
        r"(\bgroup\s+by\b)",
        r"(\bhaving\b)",
        r"(\blimit\b.*\boffset\b)",
        r"(\bwaitfor\s+delay\b)",
        r"(\bbenchmark\s*\()",
        r"(\bsleep\s*\()",
    ]
    
    @classmethod
    def detect_sql_injection(cls, input_value: str) -> bool:
        """
        检测SQL注入攻击模式
        
        Args:
            input_value: 输入值
            
        Returns:
            bool: 如果检测到SQL注入模式返回True
        """
        if not isinstance(input_value, str):
            return False
        
        # 转换为小写进行检测
        lower_input = input_value.lower()
        
        for pattern in cls.INJECTION_PATTERNS:
            if re.search(pattern, lower_input, re.IGNORECASE):
                logger.warning(f"检测到潜在SQL注入攻击: {input_value}")
                return True
        
        return False
    
    @classmethod
    def sanitize_input(cls, input_value: Any) -> Any:
        """
        清理输入数据，防止SQL注入
        
        Args:
            input_value: 输入值
            
        Returns:
            清理后的值
            
        Raises:
            SQLInjectionError: 检测到SQL注入攻击时抛出
        """
        if input_value is None:
            return None
        
        if isinstance(input_value, str):
            # 检测SQL注入
            if cls.detect_sql_injection(input_value):
                raise SQLInjectionError(f"检测到SQL注入攻击模式: {input_value}")
            
            # 基本清理：移除危险字符
            sanitized = input_value.strip()
            
            # 转义单引号和双引号
            sanitized = sanitized.replace("'", "''")
            
            return sanitized
        
        elif isinstance(input_value, (list, tuple)):
            return [cls.sanitize_input(item) for item in input_value]
        
        elif isinstance(input_value, dict):
            return {key: cls.sanitize_input(value) for key, value in input_value.items()}
        
        else:
            return input_value
    
    @classmethod
    def build_safe_filter(cls, model_class, filters: Dict[str, Any]) -> List:
        """
        构建安全的过滤条件
        
        Args:
            model_class: SQLAlchemy模型类
            filters: 过滤条件字典
            
        Returns:
            安全的过滤条件列表
        """
        safe_conditions = []
        
        for field_name, value in filters.items():
            # 验证字段名是否存在于模型中
            if not hasattr(model_class, field_name):
                logger.warning(f"模型 {model_class.__name__} 中不存在字段: {field_name}")
                continue
            
            # 清理输入值
            try:
                safe_value = cls.sanitize_input(value)
            except SQLInjectionError as e:
                logger.error(f"字段 {field_name} 的值包含SQL注入攻击: {e}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="输入包含非法字符"
                )
            
            # 获取模型字段
            field = getattr(model_class, field_name)
            
            # 构建安全的条件
            if isinstance(safe_value, (list, tuple)):
                safe_conditions.append(field.in_(safe_value))
            elif isinstance(safe_value, str) and '%' in safe_value:
                safe_conditions.append(field.like(safe_value))
            else:
                safe_conditions.append(field == safe_value)
        
        return safe_conditions

class SafeQueryExecutor:
    """安全查询执行器"""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.query_builder = SecurityQueryBuilder()
    
    def safe_get_by_id(self, model_class, item_id: Union[int, str]):
        """
        安全的按ID查询
        
        Args:
            model_class: 模型类
            item_id: 项目ID
            
        Returns:
            查询结果或None
        """
        try:
            # 验证ID类型
            if isinstance(item_id, str):
                if not item_id.isdigit():
                    raise ValueError("ID必须是数字")
                item_id = int(item_id)
            
            # 使用参数化查询
            return self.db_session.query(model_class).filter(
                model_class.id == item_id
            ).first()
            
        except (ValueError, SQLAlchemyError) as e:
            logger.error(f"安全查询失败: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的查询参数"
            )
    
    def safe_filter_query(self, model_class, filters: Dict[str, Any], 
                         limit: Optional[int] = None, 
                         offset: Optional[int] = None,
                         order_by: Optional[str] = None):
        """
        安全的过滤查询
        
        Args:
            model_class: 模型类
            filters: 过滤条件
            limit: 限制数量
            offset: 偏移量
            order_by: 排序字段
            
        Returns:
            查询结果列表
        """
        try:
            # 构建安全的过滤条件
            safe_conditions = self.query_builder.build_safe_filter(model_class, filters)
            
            # 构建查询
            query = self.db_session.query(model_class)
            
            # 应用过滤条件
            if safe_conditions:
                query = query.filter(and_(*safe_conditions))
            
            # 安全的排序
            if order_by:
                if not hasattr(model_class, order_by):
                    raise ValueError(f"排序字段 {order_by} 不存在")
                
                order_field = getattr(model_class, order_by)
                query = query.order_by(order_field)
            
            # 安全的分页
            if offset is not None:
                if offset < 0:
                    raise ValueError("偏移量不能为负数")
                query = query.offset(offset)
            
            if limit is not None:
                if limit <= 0 or limit > 1000:  # 限制最大查询数量
                    raise ValueError("限制数量必须在1-1000之间")
                query = query.limit(limit)
            
            return query.all()
            
        except (ValueError, SQLAlchemyError) as e:
            logger.error(f"安全过滤查询失败: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="查询参数无效"
            )
    
    def safe_search_query(self, model_class, search_fields: List[str], 
                         search_term: str, limit: int = 50):
        """
        安全的搜索查询
        
        Args:
            model_class: 模型类
            search_fields: 搜索字段列表
            search_term: 搜索词
            limit: 限制数量
            
        Returns:
            搜索结果列表
        """
        try:
            # 清理搜索词
            safe_search_term = self.query_builder.sanitize_input(search_term)
            
            if not safe_search_term or len(safe_search_term.strip()) < 2:
                return []
            
            # 验证搜索字段
            valid_fields = []
            for field_name in search_fields:
                if hasattr(model_class, field_name):
                    valid_fields.append(getattr(model_class, field_name))
                else:
                    logger.warning(f"搜索字段 {field_name} 不存在于模型 {model_class.__name__}")
            
            if not valid_fields:
                return []
            
            # 构建搜索条件
            search_pattern = f"%{safe_search_term}%"
            search_conditions = [field.like(search_pattern) for field in valid_fields]
            
            # 执行搜索
            query = self.db_session.query(model_class).filter(
                or_(*search_conditions)
            ).limit(min(limit, 100))  # 限制最大搜索结果
            
            return query.all()
            
        except (SQLInjectionError, SQLAlchemyError) as e:
            logger.error(f"安全搜索查询失败: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="搜索参数无效"
            )
    
    def safe_count_query(self, model_class, filters: Dict[str, Any] = None):
        """
        安全的计数查询
        
        Args:
            model_class: 模型类
            filters: 过滤条件
            
        Returns:
            符合条件的记录数量
        """
        try:
            query = self.db_session.query(model_class)
            
            if filters:
                safe_conditions = self.query_builder.build_safe_filter(model_class, filters)
                if safe_conditions:
                    query = query.filter(and_(*safe_conditions))
            
            return query.count()
            
        except (SQLInjectionError, SQLAlchemyError) as e:
            logger.error(f"安全计数查询失败: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="计数查询失败"
            )

def create_safe_query_executor(db_session: Session) -> SafeQueryExecutor:
    """
    创建安全查询执行器
    
    Args:
        db_session: 数据库会话
        
    Returns:
        SafeQueryExecutor实例
    """
    return SafeQueryExecutor(db_session)

# 装饰器：自动进行SQL注入检测
def sql_injection_protection(func):
    """
    SQL注入防护装饰器
    
    自动检测函数参数中的SQL注入攻击模式
    """
    import functools
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # 检测所有字符串参数
        for arg in args:
            if isinstance(arg, str) and SecurityQueryBuilder.detect_sql_injection(arg):
                logger.warning(f"函数 {func.__name__} 检测到SQL注入攻击: {arg}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="输入包含非法字符"
                )
        
        for key, value in kwargs.items():
            if isinstance(value, str) and SecurityQueryBuilder.detect_sql_injection(value):
                logger.warning(f"函数 {func.__name__} 参数 {key} 检测到SQL注入攻击: {value}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="输入包含非法字符"
                )
        
        return func(*args, **kwargs)
    
    return wrapper

# 输入验证和清理函数
def validate_extension_name(name: str) -> bool:
    """
    验证扩展名称，防止路径遍历攻击
    
    Args:
        name: 扩展名称
        
    Returns:
        bool: 如果名称有效返回True
        
    Raises:
        ValueError: 如果名称无效
    """
    if not name or not isinstance(name, str):
        raise ValueError("扩展名称不能为空")
    
    # 检查路径遍历攻击
    if '..' in name or '/' in name or '\\' in name:
        raise ValueError("扩展名称包含非法字符")
    
    # 检查特殊字符
    if not re.match(r'^[a-zA-Z0-9_-]+$', name):
        raise ValueError("扩展名称只能包含字母、数字、下划线和连字符")
    
    # 检查长度
    if len(name) > 100:
        raise ValueError("扩展名称过长")
    
    return True

def validate_extension_path(path: str) -> bool:
    """
    验证扩展路径，防止路径遍历攻击
    
    Args:
        path: 扩展路径
        
    Returns:
        bool: 如果路径有效返回True
        
    Raises:
        ValueError: 如果路径无效
    """
    if not path or not isinstance(path, str):
        raise ValueError("扩展路径不能为空")
    
    # 检查路径遍历攻击
    if '..' in path:
        raise ValueError("扩展路径包含非法字符")
    
    # 检查长度
    if len(path) > 500:
        raise ValueError("扩展路径过长")
    
    return True

def validate_and_sanitize_input(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    验证和清理输入数据
    
    Args:
        data: 输入数据字典
        
    Returns:
        清理后的数据字典
        
    Raises:
        HTTPException: 检测到SQL注入时抛出
    """
    # 对于某些已知安全的字段，跳过SQL注入检测
    safe_fields = {'user_agent', 'referrer', 'session_id', 'visitor_ip'}
    
    try:
        cleaned_data = {}
        for key, value in data.items():
            if key in safe_fields and isinstance(value, str):
                # 对于安全字段，只做基本清理，不进行SQL注入检测
                cleaned_data[key] = value.strip() if value else value
            else:
                # 对其他字段进行完整的安全检查
                cleaned_data[key] = SecurityQueryBuilder.sanitize_input(value)
        return cleaned_data
    except SQLInjectionError as e:
        logger.error(f"输入验证失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="输入包含非法字符"
        )

# 安全的原生SQL执行
def execute_safe_raw_sql(db_session: Session, sql_template: str, 
                        parameters: Dict[str, Any]) -> Any:
    """
    安全执行原生SQL查询
    
    Args:
        db_session: 数据库会话
        sql_template: SQL模板（使用命名参数）
        parameters: 参数字典
        
    Returns:
        查询结果
        
    Raises:
        HTTPException: SQL注入检测或执行失败时抛出
    """
    try:
        # 验证SQL模板不包含注入模式
        if SecurityQueryBuilder.detect_sql_injection(sql_template):
            raise SQLInjectionError("SQL模板包含潜在的注入攻击模式")
        
        # 清理参数
        safe_parameters = SecurityQueryBuilder.sanitize_input(parameters)
        
        # 使用参数化查询执行
        result = db_session.execute(text(sql_template), safe_parameters)
        return result.fetchall()
        
    except (SQLInjectionError, SQLAlchemyError) as e:
        logger.error(f"安全SQL执行失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="SQL查询执行失败"
        )