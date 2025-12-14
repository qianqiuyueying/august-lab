"""
速率限制中间件
防止API滥用
"""

import time
import asyncio
from collections import defaultdict
from typing import Callable
from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import logging

logger = logging.getLogger(__name__)

class RateLimitMiddleware(BaseHTTPMiddleware):
    """速率限制中间件"""
    
    def __init__(self, app, requests_per_window: int = 100, window_seconds: int = 3600):
        super().__init__(app)
        self.requests_per_window = requests_per_window
        self.window_seconds = window_seconds
        # 存储每个IP的请求时间戳
        self.request_times: dict[str, list[float]] = defaultdict(list)
        # 清理过期记录的时间间隔（秒）
        self.cleanup_interval = 300  # 5分钟
        self.last_cleanup = time.time()
        # 异步锁，保护并发访问
        self._lock = asyncio.Lock()
    
    async def _cleanup_old_records(self):
        """清理过期的请求记录"""
        current_time = time.time()
        if current_time - self.last_cleanup < self.cleanup_interval:
            return
        
        async with self._lock:
            cutoff_time = current_time - self.window_seconds
            for ip in list(self.request_times.keys()):
                # 只保留窗口内的记录
                self.request_times[ip] = [
                    timestamp for timestamp in self.request_times[ip]
                    if timestamp > cutoff_time
                ]
                # 如果列表为空，删除该IP的记录
                if not self.request_times[ip]:
                    del self.request_times[ip]
            
            self.last_cleanup = current_time
    
    def _get_client_ip(self, request: Request) -> str:
        """获取客户端IP地址"""
        # 优先从X-Forwarded-For获取（代理场景）
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            # X-Forwarded-For可能包含多个IP，取第一个
            return forwarded.split(",")[0].strip()
        
        # 从X-Real-IP获取
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # 最后从客户端获取
        if request.client:
            return request.client.host
        
        return "unknown"
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求并应用速率限制"""
        
        # 跳过健康检查端点
        if request.url.path in ["/health", "/", "/docs", "/openapi.json", "/redoc"]:
            return await call_next(request)
        
        # 定期清理过期记录
        await self._cleanup_old_records()
        
        # 获取客户端IP
        client_ip = self._get_client_ip(request)
        
        # 获取当前时间
        current_time = time.time()
        
        # 根据端点类型设置不同的限制策略
        path = request.url.path
        is_login = path == "/api/auth/login"
        
        # 登录接口使用更严格的限制（防止暴力破解）
        if is_login:
            login_limit = 10  # 每小时最多10次登录尝试
            login_window = 3600  # 1小时
            cutoff_time = current_time - login_window
            
            async with self._lock:
                # 使用单独的键来跟踪登录请求
                login_key = f"{client_ip}:login"
                login_requests = self.request_times.get(login_key, [])
                
                # 清理窗口外的记录
                login_requests[:] = [timestamp for timestamp in login_requests if timestamp > cutoff_time]
                
                # 检查是否超过登录限制
                if len(login_requests) >= login_limit:
                    logger.warning(f"登录速率限制触发: IP {client_ip} 在 {login_window} 秒内尝试登录 {len(login_requests)} 次")
                    reset_time = int(cutoff_time + login_window)
                    return JSONResponse(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        content={
                            "error": {
                                "code": "TOO_MANY_REQUESTS",
                                "message": f"登录尝试过于频繁，请稍后再试（限制：{login_limit}次/小时）",
                                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(current_time))
                            }
                        },
                        headers={
                            "X-RateLimit-Limit": str(login_limit),
                            "X-RateLimit-Remaining": "0",
                            "X-RateLimit-Reset": str(reset_time),
                            "Retry-After": str(login_window)
                        }
                    )
                
                # 记录本次登录尝试
                login_requests.append(current_time)
                self.request_times[login_key] = login_requests
                request_count = len(login_requests)
                limit_value = login_limit
                window_value = login_window
        else:
            # 其他接口使用通用限制
            cutoff_time = current_time - self.window_seconds
            limit_value = self.requests_per_window
            window_value = self.window_seconds
            
            # 使用锁保护并发访问
            async with self._lock:
                # 获取该IP的请求记录
                ip_requests = self.request_times[client_ip]
                
                # 清理窗口外的记录
                ip_requests[:] = [timestamp for timestamp in ip_requests if timestamp > cutoff_time]
                
                # 检查是否超过限制
                if len(ip_requests) >= self.requests_per_window:
                    logger.warning(f"速率限制触发: IP {client_ip} 在 {self.window_seconds} 秒内请求 {len(ip_requests)} 次")
                    # 直接返回响应，而不是抛出异常，避免应用崩溃
                    reset_time = int(cutoff_time + self.window_seconds)
                    return JSONResponse(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        content={
                            "error": {
                                "code": "TOO_MANY_REQUESTS",
                                "message": f"请求过于频繁，请在 {self.window_seconds} 秒后再试",
                                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(current_time))
                            }
                        },
                        headers={
                            "X-RateLimit-Limit": str(self.requests_per_window),
                            "X-RateLimit-Remaining": "0",
                            "X-RateLimit-Reset": str(reset_time),
                            "Retry-After": str(self.window_seconds)
                        }
                    )
                
                # 记录本次请求
                ip_requests.append(current_time)
                request_count = len(ip_requests)
        
        # 继续处理请求
        response = await call_next(request)
        
        # 添加速率限制响应头
        remaining = max(0, limit_value - request_count)
        reset_time = int(cutoff_time + window_value)
        response.headers["X-RateLimit-Limit"] = str(limit_value)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset_time)
        
        return response
