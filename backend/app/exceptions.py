"""
自定义异常类
"""

from fastapi import HTTPException, status
from typing import Any, Dict, Optional
from datetime import datetime, timezone

class ValidationError(HTTPException):
    """数据验证错误"""
    def __init__(self, detail: str, field: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error_code": "VALIDATION_ERROR",
                "message": detail,
                "field": field,
                "timestamp": datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
            }
        )

class NotFoundError(HTTPException):
    """资源未找到错误"""
    def __init__(self, resource: str, resource_id: Any = None):
        detail = f"{resource}不存在"
        if resource_id:
            detail = f"{resource} (ID: {resource_id}) 不存在"
        
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": "NOT_FOUND",
                "message": detail,
                "resource": resource,
                "resource_id": resource_id,
                "timestamp": datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
            }
        )

class AuthenticationError(HTTPException):
    """认证错误"""
    def __init__(self, detail: str = "认证失败"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error_code": "AUTHENTICATION_ERROR",
                "message": detail,
                "timestamp": datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
            }
        )

class AuthorizationError(HTTPException):
    """授权错误"""
    def __init__(self, detail: str = "权限不足"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error_code": "AUTHORIZATION_ERROR",
                "message": detail,
                "timestamp": datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
            }
        )

class DatabaseError(HTTPException):
    """数据库错误"""
    def __init__(self, detail: str = "数据库操作失败"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_code": "DATABASE_ERROR",
                "message": detail,
                "timestamp": datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
            }
        )

class FileUploadError(HTTPException):
    """文件上传错误"""
    def __init__(self, detail: str = "文件上传失败"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error_code": "FILE_UPLOAD_ERROR",
                "message": detail,
                "timestamp": datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
            }
        )

class BusinessLogicError(HTTPException):
    """业务逻辑错误"""
    def __init__(self, detail: str, error_code: str = "BUSINESS_ERROR"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error_code": error_code,
                "message": detail,
                "timestamp": datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
            }
        )