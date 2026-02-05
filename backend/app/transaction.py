"""
数据库事务处理和错误恢复模块

提供事务装饰器和错误处理机制，确保数据操作的原子性和一致性
"""

import functools
import logging
from typing import Any, Callable, TypeVar, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError
from fastapi import HTTPException, status
import time
import json

# 设置日志
logger = logging.getLogger(__name__)

F = TypeVar('F', bound=Callable[..., Any])

#region agent log
def _agent_log(payload: dict) -> None:
    """Debug-mode NDJSON logger (no secrets)."""
    try:
        payload.setdefault("timestamp", int(time.time() * 1000))
        with open(r"g:\vscode\projects\August\.cursor\debug.log", "a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    except Exception:
        pass
#endregion

class DatabaseError(Exception):
    """数据库操作异常基类"""
    pass

class TransactionError(DatabaseError):
    """事务处理异常"""
    pass

class ConnectionError(DatabaseError):
    """数据库连接异常"""
    pass

def transactional(rollback_on_exception: bool = True, max_retries: int = 3):
    """
    数据库事务装饰器
    
    Args:
        rollback_on_exception: 异常时是否回滚事务
        max_retries: 最大重试次数
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 查找Session参数
            db_session = None
            for arg in args:
                if isinstance(arg, Session):
                    db_session = arg
                    break
            
            if 'db' in kwargs and isinstance(kwargs['db'], Session):
                db_session = kwargs['db']
            
            if db_session is None:
                raise ValueError("事务装饰器需要Session参数")
            
            retry_count = 0
            while retry_count <= max_retries:
                try:
                    # 开始事务
                    #region agent log
                    _agent_log({
                        "sessionId": "debug-session",
                        "runId": "pre-fix",
                        "hypothesisId": "H1",
                        "location": "backend/app/transaction.py:transactional.wrapper:before_func",
                        "message": "enter transactional wrapper",
                        "data": {
                            "func": getattr(func, "__name__", str(func)),
                            "retry_count": retry_count,
                            "max_retries": max_retries,
                            "rollback_on_exception": rollback_on_exception,
                            "has_db_session": db_session is not None,
                        },
                    })
                    #endregion
                    result = func(*args, **kwargs)
                    
                    # 提交事务
                    #region agent log
                    _agent_log({
                        "sessionId": "debug-session",
                        "runId": "pre-fix",
                        "hypothesisId": "H1",
                        "location": "backend/app/transaction.py:transactional.wrapper:before_commit",
                        "message": "about to commit transactional session",
                        "data": {"func": getattr(func, "__name__", str(func))},
                    })
                    #endregion
                    db_session.commit()
                    logger.info(f"事务成功提交: {func.__name__}")
                    return result
                    
                except IntegrityError as e:
                    # 数据完整性错误，不重试
                    if rollback_on_exception:
                        db_session.rollback()
                        logger.error(f"数据完整性错误，事务已回滚: {func.__name__}, 错误: {str(e)}")
                    
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="数据完整性约束违反"
                    )
                
                except OperationalError as e:
                    # 操作错误，可能是连接问题，可以重试
                    if rollback_on_exception:
                        db_session.rollback()
                    
                    retry_count += 1
                    if retry_count <= max_retries:
                        logger.warning(f"数据库操作错误，正在重试 ({retry_count}/{max_retries}): {func.__name__}, 错误: {str(e)}")
                        time.sleep(0.1 * retry_count)  # 指数退避
                        continue
                    else:
                        logger.error(f"数据库操作错误，重试次数已用完: {func.__name__}, 错误: {str(e)}")
                        raise HTTPException(
                            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail="数据库服务暂时不可用"
                        )
                
                except SQLAlchemyError as e:
                    # 其他SQLAlchemy错误
                    if rollback_on_exception:
                        db_session.rollback()
                        logger.error(f"数据库错误，事务已回滚: {func.__name__}, 错误: {str(e)}")
                    
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="数据库操作失败"
                    )
                
                except HTTPException:
                    # HTTP异常应该直接重新抛出，不要转换
                    if rollback_on_exception:
                        db_session.rollback()
                    raise
                
                except Exception as e:
                    # 其他异常
                    if rollback_on_exception:
                        db_session.rollback()
                    
                    #region agent log
                    _agent_log({
                        "sessionId": "debug-session",
                        "runId": "pre-fix",
                        "hypothesisId": "H1",
                        "location": "backend/app/transaction.py:transactional.wrapper:except_exception",
                        "message": "caught exception in transactional wrapper",
                        "data": {
                            "func": getattr(func, "__name__", str(func)),
                            "exc_type": type(e).__name__,
                            "is_http_exception": isinstance(e, HTTPException),
                            "http_status_code": getattr(e, "status_code", None),
                            "http_detail_type": type(getattr(e, "detail", None)).__name__,
                        },
                    })
                    #endregion
                    
                    # 记录详细的异常信息
                    import traceback
                    error_msg = str(e) if str(e) else repr(e)
                    error_traceback = traceback.format_exc()
                    logger.error(f"未知错误，事务已回滚: {func.__name__}, 错误: {error_msg}\n{error_traceback}")
                    
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"服务器内部错误: {error_msg}"
                    )
        
        return wrapper
    return decorator

def with_db_error_handling(func: F) -> F:
    """
    数据库错误处理装饰器
    
    用于处理数据库连接和操作错误，提供统一的错误响应
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        
        except HTTPException:
            # 重新抛出HTTP异常
            raise
        
        except IntegrityError as e:
            logger.error(f"数据完整性错误: {func.__name__}, 错误: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="数据完整性约束违反"
            )
        
        except OperationalError as e:
            logger.error(f"数据库操作错误: {func.__name__}, 错误: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="数据库服务暂时不可用"
            )
        
        except SQLAlchemyError as e:
            logger.error(f"数据库错误: {func.__name__}, 错误: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="数据库操作失败"
            )
        
        except Exception as e:
            logger.error(f"未知错误: {func.__name__}, 错误: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="服务器内部错误"
            )
    
    return wrapper

class DatabaseConnectionManager:
    """数据库连接管理器"""
    
    def __init__(self, engine, max_retries: int = 3, retry_delay: float = 1.0):
        self.engine = engine
        self.max_retries = max_retries
        self.retry_delay = retry_delay
    
    def test_connection(self) -> bool:
        """测试数据库连接"""
        try:
            with self.engine.connect() as connection:
                connection.execute("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"数据库连接测试失败: {str(e)}")
            return False
    
    def ensure_connection(self) -> bool:
        """确保数据库连接可用，支持重试"""
        for attempt in range(self.max_retries + 1):
            if self.test_connection():
                if attempt > 0:
                    logger.info(f"数据库连接在第 {attempt + 1} 次尝试后恢复")
                return True
            
            if attempt < self.max_retries:
                logger.warning(f"数据库连接失败，正在重试 ({attempt + 1}/{self.max_retries})")
                time.sleep(self.retry_delay * (attempt + 1))
        
        logger.error("数据库连接失败，已达到最大重试次数")
        return False
    
    def get_session_with_retry(self, session_factory):
        """获取数据库会话，支持连接重试"""
        if not self.ensure_connection():
            raise ConnectionError("无法建立数据库连接")
        
        try:
            return session_factory()
        except Exception as e:
            logger.error(f"创建数据库会话失败: {str(e)}")
            raise ConnectionError(f"创建数据库会话失败: {str(e)}")

def create_safe_db_dependency(engine, session_factory):
    """
    创建安全的数据库依赖，包含连接重试和错误处理
    """
    connection_manager = DatabaseConnectionManager(engine)
    
    def get_db_safe():
        """安全的数据库会话获取函数"""
        db = None
        try:
            db = connection_manager.get_session_with_retry(session_factory)
            yield db
        except ConnectionError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="数据库服务暂时不可用"
            )
        except Exception as e:
            logger.error(f"数据库会话错误: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="数据库服务错误"
            )
        finally:
            if db:
                try:
                    db.close()
                except Exception as e:
                    logger.error(f"关闭数据库会话时出错: {str(e)}")
    
    return get_db_safe

# 批量操作事务处理
class BatchTransaction:
    """批量操作事务管理器"""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.operations = []
        self.completed_operations = []
    
    def add_operation(self, operation: Callable, *args, **kwargs):
        """添加操作到批量事务中"""
        self.operations.append((operation, args, kwargs))
    
    def execute_all(self, rollback_on_failure: bool = True) -> list:
        """执行所有操作"""
        results = []
        
        try:
            for operation, args, kwargs in self.operations:
                result = operation(*args, **kwargs)
                results.append(result)
                self.completed_operations.append((operation, args, kwargs))
            
            # 提交所有操作
            self.db_session.commit()
            logger.info(f"批量事务成功提交，共 {len(self.operations)} 个操作")
            return results
            
        except Exception as e:
            if rollback_on_failure:
                self.db_session.rollback()
                logger.error(f"批量事务失败，已回滚。已完成 {len(self.completed_operations)}/{len(self.operations)} 个操作")
            
            raise TransactionError(f"批量事务执行失败: {str(e)}")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.db_session.rollback()
            logger.error(f"批量事务上下文异常，已回滚: {exc_val}")
        return False