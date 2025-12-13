"""
API错误处理和响应标准化模块

提供统一的错误响应格式和异常处理器
"""

import logging
import traceback
from typing import Any, Dict, Optional, Union
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError
from pydantic import ValidationError
import uuid

logger = logging.getLogger(__name__)

class APIErrorCode:
    """API错误代码常量"""
    
    # 通用错误
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    BAD_REQUEST = "BAD_REQUEST"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    NOT_FOUND = "NOT_FOUND"
    METHOD_NOT_ALLOWED = "METHOD_NOT_ALLOWED"
    CONFLICT = "CONFLICT"
    UNPROCESSABLE_ENTITY = "UNPROCESSABLE_ENTITY"
    TOO_MANY_REQUESTS = "TOO_MANY_REQUESTS"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    
    # 验证错误
    VALIDATION_ERROR = "VALIDATION_ERROR"
    FIELD_VALIDATION_ERROR = "FIELD_VALIDATION_ERROR"
    
    # 数据库错误
    DATABASE_ERROR = "DATABASE_ERROR"
    DATABASE_CONNECTION_ERROR = "DATABASE_CONNECTION_ERROR"
    DATA_INTEGRITY_ERROR = "DATA_INTEGRITY_ERROR"
    
    # 认证错误
    AUTHENTICATION_FAILED = "AUTHENTICATION_FAILED"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    TOKEN_INVALID = "TOKEN_INVALID"
    
    # 业务逻辑错误
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    RESOURCE_ALREADY_EXISTS = "RESOURCE_ALREADY_EXISTS"
    OPERATION_NOT_ALLOWED = "OPERATION_NOT_ALLOWED"
    
    # 文件处理错误
    FILE_UPLOAD_ERROR = "FILE_UPLOAD_ERROR"
    FILE_SIZE_EXCEEDED = "FILE_SIZE_EXCEEDED"
    FILE_TYPE_NOT_SUPPORTED = "FILE_TYPE_NOT_SUPPORTED"
    
    # 安全错误
    SQL_INJECTION_DETECTED = "SQL_INJECTION_DETECTED"
    MALICIOUS_INPUT_DETECTED = "MALICIOUS_INPUT_DETECTED"

class StandardAPIError(Exception):
    """标准API异常基类"""
    
    def __init__(
        self,
        message: str,
        error_code: str = APIErrorCode.INTERNAL_SERVER_ERROR,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None,
        error_id: Optional[str] = None
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        self.error_id = error_id or str(uuid.uuid4())
        self.timestamp = datetime.utcnow()
        super().__init__(self.message)

class ValidationAPIError(StandardAPIError):
    """验证错误"""
    
    def __init__(self, message: str, field_errors: Optional[Dict[str, str]] = None):
        super().__init__(
            message=message,
            error_code=APIErrorCode.VALIDATION_ERROR,
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"field_errors": field_errors} if field_errors else None
        )

class AuthenticationAPIError(StandardAPIError):
    """认证错误"""
    
    def __init__(self, message: str = "认证失败"):
        super().__init__(
            message=message,
            error_code=APIErrorCode.AUTHENTICATION_FAILED,
            status_code=status.HTTP_401_UNAUTHORIZED
        )

class AuthorizationAPIError(StandardAPIError):
    """授权错误"""
    
    def __init__(self, message: str = "权限不足"):
        super().__init__(
            message=message,
            error_code=APIErrorCode.FORBIDDEN,
            status_code=status.HTTP_403_FORBIDDEN
        )

class ResourceNotFoundAPIError(StandardAPIError):
    """资源未找到错误"""
    
    def __init__(self, resource_type: str, resource_id: Union[str, int] = None):
        message = f"{resource_type}不存在"
        if resource_id:
            message += f"（ID: {resource_id}）"
        
        super().__init__(
            message=message,
            error_code=APIErrorCode.RESOURCE_NOT_FOUND,
            status_code=status.HTTP_404_NOT_FOUND,
            details={"resource_type": resource_type, "resource_id": resource_id}
        )

class DatabaseAPIError(StandardAPIError):
    """数据库错误"""
    
    def __init__(self, message: str = "数据库操作失败", original_error: Optional[Exception] = None):
        details = {}
        if original_error:
            details["original_error"] = str(original_error)
        
        super().__init__(
            message=message,
            error_code=APIErrorCode.DATABASE_ERROR,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details
        )

class SecurityAPIError(StandardAPIError):
    """安全错误"""
    
    def __init__(self, message: str = "检测到安全威胁", threat_type: str = "unknown"):
        super().__init__(
            message=message,
            error_code=APIErrorCode.MALICIOUS_INPUT_DETECTED,
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"threat_type": threat_type}
        )

def create_error_response(
    error_code: str,
    message: str,
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    details: Optional[Dict[str, Any]] = None,
    error_id: Optional[str] = None,
    request_id: Optional[str] = None
) -> JSONResponse:
    """
    创建标准化的错误响应
    
    Args:
        error_code: 错误代码
        message: 错误消息
        status_code: HTTP状态码
        details: 错误详情
        error_id: 错误ID
        request_id: 请求ID
        
    Returns:
        JSONResponse: 标准化的错误响应
    """
    error_response = {
        "error": {
            "code": error_code,
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
            "error_id": error_id or str(uuid.uuid4())
        }
    }
    
    if details:
        error_response["error"]["details"] = details
    
    if request_id:
        error_response["error"]["request_id"] = request_id
    
    return JSONResponse(
        status_code=status_code,
        content=error_response
    )

def setup_error_handlers(app: FastAPI):
    """
    设置全局错误处理器
    
    Args:
        app: FastAPI应用实例
    """
    
    @app.exception_handler(StandardAPIError)
    async def standard_api_error_handler(request: Request, exc: StandardAPIError):
        """标准API错误处理器"""
        logger.error(f"API错误 [{exc.error_id}]: {exc.message}", exc_info=True)
        
        return create_error_response(
            error_code=exc.error_code,
            message=exc.message,
            status_code=exc.status_code,
            details=exc.details,
            error_id=exc.error_id,
            request_id=getattr(request.state, 'request_id', None)
        )
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """HTTP异常处理器"""
        error_code_map = {
            400: APIErrorCode.BAD_REQUEST,
            401: APIErrorCode.UNAUTHORIZED,
            403: APIErrorCode.FORBIDDEN,
            404: APIErrorCode.NOT_FOUND,
            405: APIErrorCode.METHOD_NOT_ALLOWED,
            409: APIErrorCode.CONFLICT,
            422: APIErrorCode.UNPROCESSABLE_ENTITY,
            429: APIErrorCode.TOO_MANY_REQUESTS,
            500: APIErrorCode.INTERNAL_SERVER_ERROR,
            503: APIErrorCode.SERVICE_UNAVAILABLE,
        }
        
        error_code = error_code_map.get(exc.status_code, APIErrorCode.INTERNAL_SERVER_ERROR)
        
        logger.warning(f"HTTP异常: {exc.status_code} - {exc.detail}")
        
        return create_error_response(
            error_code=error_code,
            message=exc.detail,
            status_code=exc.status_code,
            request_id=getattr(request.state, 'request_id', None)
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """请求验证错误处理器"""
        field_errors = {}
        
        for error in exc.errors():
            field_path = " -> ".join(str(loc) for loc in error["loc"])
            field_errors[field_path] = error["msg"]
        
        logger.warning(f"请求验证错误: {field_errors}")
        
        return create_error_response(
            error_code=APIErrorCode.FIELD_VALIDATION_ERROR,
            message="请求数据验证失败",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details={"field_errors": field_errors},
            request_id=getattr(request.state, 'request_id', None)
        )
    
    @app.exception_handler(ValidationError)
    async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
        """Pydantic验证错误处理器"""
        field_errors = {}
        
        for error in exc.errors():
            field_path = " -> ".join(str(loc) for loc in error["loc"])
            field_errors[field_path] = error["msg"]
        
        logger.warning(f"数据验证错误: {field_errors}")
        
        return create_error_response(
            error_code=APIErrorCode.VALIDATION_ERROR,
            message="数据验证失败",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"field_errors": field_errors},
            request_id=getattr(request.state, 'request_id', None)
        )
    
    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(request: Request, exc: IntegrityError):
        """数据完整性错误处理器"""
        logger.error(f"数据完整性错误: {str(exc)}")
        
        # 解析常见的完整性约束错误
        error_message = "数据完整性约束违反"
        details = {"constraint_type": "unknown"}
        
        if "UNIQUE constraint failed" in str(exc):
            error_message = "数据已存在，违反唯一性约束"
            details["constraint_type"] = "unique"
        elif "FOREIGN KEY constraint failed" in str(exc):
            error_message = "外键约束违反"
            details["constraint_type"] = "foreign_key"
        elif "NOT NULL constraint failed" in str(exc):
            error_message = "必填字段不能为空"
            details["constraint_type"] = "not_null"
        
        return create_error_response(
            error_code=APIErrorCode.DATA_INTEGRITY_ERROR,
            message=error_message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details,
            request_id=getattr(request.state, 'request_id', None)
        )
    
    @app.exception_handler(OperationalError)
    async def operational_error_handler(request: Request, exc: OperationalError):
        """数据库操作错误处理器"""
        logger.error(f"数据库操作错误: {str(exc)}")
        
        return create_error_response(
            error_code=APIErrorCode.DATABASE_CONNECTION_ERROR,
            message="数据库服务暂时不可用",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            request_id=getattr(request.state, 'request_id', None)
        )
    
    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
        """SQLAlchemy错误处理器"""
        logger.error(f"数据库错误: {str(exc)}")
        
        return create_error_response(
            error_code=APIErrorCode.DATABASE_ERROR,
            message="数据库操作失败",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            request_id=getattr(request.state, 'request_id', None)
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """通用异常处理器"""
        error_id = str(uuid.uuid4())
        
        logger.error(
            f"未处理的异常 [{error_id}]: {str(exc)}\n{traceback.format_exc()}"
        )
        
        # 在生产环境中不暴露详细的错误信息
        return create_error_response(
            error_code=APIErrorCode.INTERNAL_SERVER_ERROR,
            message="服务器内部错误",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_id=error_id,
            request_id=getattr(request.state, 'request_id', None)
        )

# 中间件：为每个请求添加请求ID
async def request_id_middleware(request: Request, call_next):
    """
    请求ID中间件
    
    为每个请求生成唯一的请求ID，用于日志追踪
    """
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    # 添加请求ID到响应头
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    
    return response

# 成功响应标准化
def create_success_response(
    data: Any = None,
    message: str = "操作成功",
    status_code: int = status.HTTP_200_OK,
    meta: Optional[Dict[str, Any]] = None
) -> JSONResponse:
    """
    创建标准化的成功响应
    
    Args:
        data: 响应数据
        message: 成功消息
        status_code: HTTP状态码
        meta: 元数据（如分页信息）
        
    Returns:
        JSONResponse: 标准化的成功响应
    """
    response_content = {
        "success": True,
        "message": message,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if data is not None:
        response_content["data"] = data
    
    if meta:
        response_content["meta"] = meta
    
    return JSONResponse(
        status_code=status_code,
        content=response_content
    )

# 分页响应标准化
def create_paginated_response(
    items: list,
    total: int,
    page: int = 1,
    page_size: int = 20,
    message: str = "查询成功"
) -> JSONResponse:
    """
    创建标准化的分页响应
    
    Args:
        items: 数据项列表
        total: 总数量
        page: 当前页码
        page_size: 每页大小
        message: 成功消息
        
    Returns:
        JSONResponse: 标准化的分页响应
    """
    total_pages = (total + page_size - 1) // page_size
    
    meta = {
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }
    }
    
    return create_success_response(
        data=items,
        message=message,
        meta=meta
    )