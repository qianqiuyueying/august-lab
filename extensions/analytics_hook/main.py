"""
产品访问分析钩子扩展
自动收集和分析产品使用数据
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from app.services.product_extension_service import (
    ProductHook, ExtensionMetadata, ExtensionType, HookType
)
from typing import Dict, Any
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class ProductAccessHook(ProductHook):
    """产品访问钩子"""
    
    def get_metadata(self) -> ExtensionMetadata:
        return ExtensionMetadata(
            name="product_access_hook",
            version="1.0.0",
            description="产品访问分析钩子",
            author="Analytics Team",
            extension_type=ExtensionType.HOOK,
            dependencies=[],
            config_schema={
                "type": "object",
                "properties": {
                    "enable_detailed_tracking": {
                        "type": "boolean",
                        "default": True,
                        "description": "是否启用详细跟踪"
                    },
                    "track_user_interactions": {
                        "type": "boolean",
                        "default": True,
                        "description": "是否跟踪用户交互"
                    },
                    "anonymize_ip": {
                        "type": "boolean",
                        "default": True,
                        "description": "是否匿名化IP地址"
                    }
                }
            }
        )
    
    def get_hook_type(self) -> HookType:
        return HookType.ON_ACCESS
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行访问分析"""
        try:
            product_id = context.get('product_id')
            request_info = context.get('request_info', {})
            
            # 收集访问数据
            access_data = {
                'product_id': product_id,
                'timestamp': datetime.utcnow().isoformat(),
                'ip_address': self._anonymize_ip(request_info.get('ip_address')) if self.config.get('anonymize_ip', True) else request_info.get('ip_address'),
                'user_agent': request_info.get('user_agent'),
                'referrer': request_info.get('referrer'),
                'session_id': request_info.get('session_id'),
                'device_info': self._extract_device_info(request_info.get('user_agent', ''))
            }
            
            # 如果启用详细跟踪，收集更多信息
            if self.config.get('enable_detailed_tracking', True):
                access_data.update({
                    'screen_resolution': request_info.get('screen_resolution'),
                    'viewport_size': request_info.get('viewport_size'),
                    'language': request_info.get('language'),
                    'timezone': request_info.get('timezone')
                })
            
            # 记录访问日志
            logger.info(f"产品访问记录: {json.dumps(access_data, ensure_ascii=False)}")
            
            # 将分析数据添加到上下文中
            context['analytics_data'] = access_data
            context['tracking_enabled'] = True
            
            return context
            
        except Exception as e:
            logger.error(f"产品访问分析失败: {str(e)}")
            return context
    
    def _anonymize_ip(self, ip_address: str) -> str:
        """匿名化IP地址"""
        if not ip_address:
            return ""
        
        try:
            # IPv4地址匿名化（保留前3段）
            if '.' in ip_address and ip_address.count('.') == 3:
                parts = ip_address.split('.')
                return f"{parts[0]}.{parts[1]}.{parts[2]}.0"
            
            # IPv6地址匿名化（保留前4段）
            if ':' in ip_address:
                parts = ip_address.split(':')
                if len(parts) >= 4:
                    return ':'.join(parts[:4]) + '::0'
            
            return "anonymized"
        except:
            return "anonymized"
    
    def _extract_device_info(self, user_agent: str) -> Dict[str, str]:
        """从User-Agent提取设备信息"""
        device_info = {
            'type': 'unknown',
            'os': 'unknown',
            'browser': 'unknown'
        }
        
        if not user_agent:
            return device_info
        
        user_agent_lower = user_agent.lower()
        
        # 检测设备类型
        if any(mobile in user_agent_lower for mobile in ['mobile', 'android', 'iphone', 'ipad']):
            device_info['type'] = 'mobile'
        elif 'tablet' in user_agent_lower or 'ipad' in user_agent_lower:
            device_info['type'] = 'tablet'
        else:
            device_info['type'] = 'desktop'
        
        # 检测操作系统
        if 'windows' in user_agent_lower:
            device_info['os'] = 'Windows'
        elif 'mac' in user_agent_lower:
            device_info['os'] = 'macOS'
        elif 'linux' in user_agent_lower:
            device_info['os'] = 'Linux'
        elif 'android' in user_agent_lower:
            device_info['os'] = 'Android'
        elif 'ios' in user_agent_lower or 'iphone' in user_agent_lower or 'ipad' in user_agent_lower:
            device_info['os'] = 'iOS'
        
        # 检测浏览器
        if 'chrome' in user_agent_lower:
            device_info['browser'] = 'Chrome'
        elif 'firefox' in user_agent_lower:
            device_info['browser'] = 'Firefox'
        elif 'safari' in user_agent_lower:
            device_info['browser'] = 'Safari'
        elif 'edge' in user_agent_lower:
            device_info['browser'] = 'Edge'
        
        return device_info


class ProductUploadHook(ProductHook):
    """产品上传钩子"""
    
    def get_metadata(self) -> ExtensionMetadata:
        return ExtensionMetadata(
            name="product_upload_hook",
            version="1.0.0",
            description="产品上传分析钩子",
            author="Analytics Team",
            extension_type=ExtensionType.HOOK,
            dependencies=[],
            config_schema={}
        )
    
    def get_hook_type(self) -> HookType:
        return HookType.AFTER_UPLOAD
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行上传后分析"""
        try:
            product_id = context.get('product_id')
            upload_info = context.get('upload_info', {})
            
            # 分析上传的文件
            file_analysis = {
                'product_id': product_id,
                'timestamp': datetime.utcnow().isoformat(),
                'file_count': upload_info.get('file_count', 0),
                'total_size': upload_info.get('total_size', 0),
                'file_types': upload_info.get('file_types', []),
                'has_entry_file': upload_info.get('has_entry_file', False),
                'complexity_score': self._calculate_complexity_score(upload_info)
            }
            
            # 记录分析结果
            logger.info(f"产品上传分析: {json.dumps(file_analysis, ensure_ascii=False)}")
            
            # 将分析结果添加到上下文
            context['upload_analysis'] = file_analysis
            
            return context
            
        except Exception as e:
            logger.error(f"产品上传分析失败: {str(e)}")
            return context
    
    def _calculate_complexity_score(self, upload_info: Dict[str, Any]) -> int:
        """计算产品复杂度评分"""
        score = 0
        
        # 基于文件数量
        file_count = upload_info.get('file_count', 0)
        if file_count > 50:
            score += 3
        elif file_count > 20:
            score += 2
        elif file_count > 5:
            score += 1
        
        # 基于文件大小
        total_size = upload_info.get('total_size', 0)
        if total_size > 10 * 1024 * 1024:  # 10MB
            score += 3
        elif total_size > 5 * 1024 * 1024:  # 5MB
            score += 2
        elif total_size > 1024 * 1024:  # 1MB
            score += 1
        
        # 基于文件类型多样性
        file_types = upload_info.get('file_types', [])
        unique_types = len(set(file_types))
        if unique_types > 10:
            score += 3
        elif unique_types > 5:
            score += 2
        elif unique_types > 2:
            score += 1
        
        return min(score, 10)  # 最高10分


class ProductErrorHook(ProductHook):
    """产品错误钩子"""
    
    def get_metadata(self) -> ExtensionMetadata:
        return ExtensionMetadata(
            name="product_error_hook",
            version="1.0.0",
            description="产品错误分析钩子",
            author="Analytics Team",
            extension_type=ExtensionType.HOOK,
            dependencies=[],
            config_schema={}
        )
    
    def get_hook_type(self) -> HookType:
        return HookType.ON_ERROR
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行错误分析"""
        try:
            product_id = context.get('product_id')
            error_info = context.get('error_info', {})
            
            # 分析错误信息
            error_analysis = {
                'product_id': product_id,
                'timestamp': datetime.utcnow().isoformat(),
                'error_type': error_info.get('error_type', 'unknown'),
                'error_message': error_info.get('error_message', ''),
                'error_code': error_info.get('error_code'),
                'stack_trace': error_info.get('stack_trace'),
                'severity': self._determine_error_severity(error_info),
                'category': self._categorize_error(error_info)
            }
            
            # 记录错误分析
            logger.error(f"产品错误分析: {json.dumps(error_analysis, ensure_ascii=False)}")
            
            # 将分析结果添加到上下文
            context['error_analysis'] = error_analysis
            
            # 如果是严重错误，添加告警标记
            if error_analysis['severity'] == 'critical':
                context['requires_alert'] = True
            
            return context
            
        except Exception as e:
            logger.error(f"产品错误分析失败: {str(e)}")
            return context
    
    def _determine_error_severity(self, error_info: Dict[str, Any]) -> str:
        """确定错误严重程度"""
        error_type = error_info.get('error_type', '').lower()
        error_message = error_info.get('error_message', '').lower()
        
        # 严重错误
        critical_indicators = [
            'security', 'authentication', 'authorization', 'sql injection',
            'xss', 'csrf', 'memory', 'crash', 'fatal'
        ]
        
        if any(indicator in error_type or indicator in error_message 
               for indicator in critical_indicators):
            return 'critical'
        
        # 高级错误
        high_indicators = [
            'database', 'connection', 'timeout', 'permission', 'access denied'
        ]
        
        if any(indicator in error_type or indicator in error_message 
               for indicator in high_indicators):
            return 'high'
        
        # 中级错误
        medium_indicators = [
            'validation', 'format', 'parsing', 'not found'
        ]
        
        if any(indicator in error_type or indicator in error_message 
               for indicator in medium_indicators):
            return 'medium'
        
        return 'low'
    
    def _categorize_error(self, error_info: Dict[str, Any]) -> str:
        """错误分类"""
        error_type = error_info.get('error_type', '').lower()
        error_message = error_info.get('error_message', '').lower()
        
        categories = {
            'security': ['security', 'authentication', 'authorization', 'xss', 'csrf', 'injection'],
            'database': ['database', 'sql', 'connection', 'query'],
            'network': ['network', 'timeout', 'connection', 'http', 'api'],
            'validation': ['validation', 'format', 'parsing', 'invalid'],
            'permission': ['permission', 'access', 'forbidden', 'unauthorized'],
            'system': ['memory', 'disk', 'cpu', 'resource', 'limit'],
            'application': ['logic', 'business', 'workflow', 'process']
        }
        
        for category, keywords in categories.items():
            if any(keyword in error_type or keyword in error_message 
                   for keyword in keywords):
                return category
        
        return 'other'