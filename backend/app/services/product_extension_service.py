"""
产品扩展机制服务
实现产品插件系统、自定义产品类型支持、功能扩展和定制选项
"""

import os
import json
import importlib
import inspect
from pathlib import Path
from typing import Dict, List, Any, Optional, Type, Callable, Union
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ExtensionType(Enum):
    """扩展类型枚举"""
    PRODUCT_TYPE = "product_type"
    RENDERER = "renderer"
    VALIDATOR = "validator"
    PROCESSOR = "processor"
    HOOK = "hook"
    MIDDLEWARE = "middleware"


class HookType(Enum):
    """钩子类型枚举"""
    BEFORE_UPLOAD = "before_upload"
    AFTER_UPLOAD = "after_upload"
    BEFORE_LAUNCH = "before_launch"
    AFTER_LAUNCH = "after_launch"
    BEFORE_DELETE = "before_delete"
    AFTER_DELETE = "after_delete"
    ON_ERROR = "on_error"
    ON_ACCESS = "on_access"


@dataclass
class ExtensionMetadata:
    """扩展元数据"""
    name: str
    version: str
    description: str
    author: str
    extension_type: ExtensionType
    dependencies: List[str]
    config_schema: Dict[str, Any]
    enabled: bool = True
    
    def to_dict(self):
        return {
            **asdict(self),
            'extension_type': self.extension_type.value
        }


@dataclass
class ProductTypeDefinition:
    """产品类型定义"""
    type_name: str
    display_name: str
    description: str
    file_extensions: List[str]
    entry_files: List[str]
    config_schema: Dict[str, Any]
    renderer_class: Optional[str] = None
    validator_class: Optional[str] = None
    
    def to_dict(self):
        return asdict(self)


class BaseExtension(ABC):
    """扩展基类"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.metadata: Optional[ExtensionMetadata] = None
    
    @abstractmethod
    def get_metadata(self) -> ExtensionMetadata:
        """获取扩展元数据"""
        pass
    
    def initialize(self) -> bool:
        """初始化扩展"""
        return True
    
    def cleanup(self) -> bool:
        """清理扩展资源"""
        return True
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """验证配置"""
        return True


class ProductTypeExtension(BaseExtension):
    """产品类型扩展基类"""
    
    @abstractmethod
    def get_product_type_definition(self) -> ProductTypeDefinition:
        """获取产品类型定义"""
        pass
    
    @abstractmethod
    def validate_product_files(self, files: Dict[str, bytes]) -> tuple[bool, str]:
        """验证产品文件"""
        pass
    
    def process_product_files(self, files: Dict[str, bytes]) -> Dict[str, bytes]:
        """处理产品文件（可选）"""
        return files
    
    def get_launch_config(self, product_config: Dict[str, Any]) -> Dict[str, Any]:
        """获取启动配置（可选）"""
        return {}


class ProductRenderer(BaseExtension):
    """产品渲染器基类"""
    
    @abstractmethod
    def render_product(self, product_id: int, config: Dict[str, Any]) -> str:
        """渲染产品HTML"""
        pass
    
    def get_required_assets(self) -> List[str]:
        """获取所需资源文件"""
        return []


class ProductValidator(BaseExtension):
    """产品验证器基类"""
    
    @abstractmethod
    def validate_product(self, product_data: Dict[str, Any], files: Dict[str, bytes]) -> tuple[bool, List[str]]:
        """验证产品"""
        pass


class ProductProcessor(BaseExtension):
    """产品处理器基类"""
    
    @abstractmethod
    def process_product(self, product_data: Dict[str, Any], files: Dict[str, bytes]) -> tuple[Dict[str, Any], Dict[str, bytes]]:
        """处理产品数据和文件"""
        pass


class ProductHook(BaseExtension):
    """产品钩子基类"""
    
    @abstractmethod
    def get_hook_type(self) -> HookType:
        """获取钩子类型"""
        pass
    
    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行钩子"""
        pass


class ProductMiddleware(BaseExtension):
    """产品中间件基类"""
    
    @abstractmethod
    def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理请求"""
        pass
    
    def process_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理响应（可选）"""
        return response_data


class ExtensionRegistry:
    """扩展注册表"""
    
    def __init__(self):
        self.extensions: Dict[str, BaseExtension] = {}
        self.product_types: Dict[str, ProductTypeExtension] = {}
        self.renderers: Dict[str, ProductRenderer] = {}
        self.validators: Dict[str, ProductValidator] = {}
        self.processors: Dict[str, ProductProcessor] = {}
        self.hooks: Dict[HookType, List[ProductHook]] = {}
        self.middlewares: List[ProductMiddleware] = []
    
    def register_extension(self, extension: BaseExtension) -> bool:
        """注册扩展"""
        try:
            metadata = extension.get_metadata()
            
            # 检查依赖
            if not self._check_dependencies(metadata.dependencies):
                logger.error(f"扩展 {metadata.name} 依赖检查失败")
                return False
            
            # 验证配置
            if not extension.validate_config(extension.config):
                logger.error(f"扩展 {metadata.name} 配置验证失败")
                return False
            
            # 初始化扩展
            if not extension.initialize():
                logger.error(f"扩展 {metadata.name} 初始化失败")
                return False
            
            # 根据类型注册到相应的集合
            self.extensions[metadata.name] = extension
            
            if isinstance(extension, ProductTypeExtension):
                type_def = extension.get_product_type_definition()
                self.product_types[type_def.type_name] = extension
            elif isinstance(extension, ProductRenderer):
                self.renderers[metadata.name] = extension
            elif isinstance(extension, ProductValidator):
                self.validators[metadata.name] = extension
            elif isinstance(extension, ProductProcessor):
                self.processors[metadata.name] = extension
            elif isinstance(extension, ProductHook):
                hook_type = extension.get_hook_type()
                if hook_type not in self.hooks:
                    self.hooks[hook_type] = []
                self.hooks[hook_type].append(extension)
            elif isinstance(extension, ProductMiddleware):
                self.middlewares.append(extension)
            
            logger.info(f"扩展 {metadata.name} 注册成功")
            return True
            
        except Exception as e:
            logger.error(f"注册扩展失败: {str(e)}")
            return False
    
    def unregister_extension(self, name: str) -> bool:
        """注销扩展"""
        try:
            if name not in self.extensions:
                return False
            
            extension = self.extensions[name]
            
            # 清理扩展资源
            extension.cleanup()
            
            # 从各个集合中移除
            del self.extensions[name]
            
            if isinstance(extension, ProductTypeExtension):
                type_def = extension.get_product_type_definition()
                if type_def.type_name in self.product_types:
                    del self.product_types[type_def.type_name]
            elif isinstance(extension, ProductRenderer):
                if name in self.renderers:
                    del self.renderers[name]
            elif isinstance(extension, ProductValidator):
                if name in self.validators:
                    del self.validators[name]
            elif isinstance(extension, ProductProcessor):
                if name in self.processors:
                    del self.processors[name]
            elif isinstance(extension, ProductHook):
                hook_type = extension.get_hook_type()
                if hook_type in self.hooks:
                    self.hooks[hook_type] = [h for h in self.hooks[hook_type] if h != extension]
            elif isinstance(extension, ProductMiddleware):
                self.middlewares = [m for m in self.middlewares if m != extension]
            
            logger.info(f"扩展 {name} 注销成功")
            return True
            
        except Exception as e:
            logger.error(f"注销扩展失败: {str(e)}")
            return False
    
    def get_extension(self, name: str) -> Optional[BaseExtension]:
        """获取扩展"""
        return self.extensions.get(name)
    
    def get_product_type_extension(self, type_name: str) -> Optional[ProductTypeExtension]:
        """获取产品类型扩展"""
        return self.product_types.get(type_name)
    
    def get_available_product_types(self) -> List[ProductTypeDefinition]:
        """获取可用的产品类型"""
        types = []
        for extension in self.product_types.values():
            types.append(extension.get_product_type_definition())
        return types
    
    def execute_hooks(self, hook_type: HookType, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行钩子"""
        if hook_type not in self.hooks:
            return context
        
        result_context = context.copy()
        
        for hook in self.hooks[hook_type]:
            try:
                result_context = hook.execute(result_context)
            except Exception as e:
                logger.error(f"执行钩子 {hook.get_metadata().name} 失败: {str(e)}")
        
        return result_context
    
    def process_middlewares(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理中间件"""
        result_data = request_data.copy()
        
        for middleware in self.middlewares:
            try:
                result_data = middleware.process_request(result_data)
            except Exception as e:
                logger.error(f"处理中间件 {middleware.get_metadata().name} 失败: {str(e)}")
        
        return result_data
    
    def _check_dependencies(self, dependencies: List[str]) -> bool:
        """检查依赖"""
        for dep in dependencies:
            if dep not in self.extensions:
                return False
        return True


class ProductExtensionService:
    """产品扩展服务"""
    
    def __init__(self, extensions_dir: str = "extensions"):
        self.extensions_dir = Path(extensions_dir)
        self.extensions_dir.mkdir(exist_ok=True)
        
        self.registry = ExtensionRegistry()
        self.config_file = self.extensions_dir / "config.json"
        self.extension_configs = self._load_extension_configs()
    
    def _load_extension_configs(self) -> Dict[str, Any]:
        """加载扩展配置"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"加载扩展配置失败: {str(e)}")
        
        return {}
    
    def _save_extension_configs(self):
        """保存扩展配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.extension_configs, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"保存扩展配置失败: {str(e)}")
    
    def load_extensions_from_directory(self) -> int:
        """从目录加载扩展"""
        loaded_count = 0
        
        # 确保扩展目录存在
        if not self.extensions_dir.exists():
            self.extensions_dir.mkdir(parents=True, exist_ok=True)
            return 0
        
        for ext_dir in self.extensions_dir.iterdir():
            # 跳过隐藏目录和文件
            if ext_dir.name.startswith('.'):
                continue
            
            # 只处理目录
            if not ext_dir.is_dir():
                continue
            
            # 验证目录名称安全性
            import re
            if not re.match(r'^[a-zA-Z0-9_-]+$', ext_dir.name):
                logger.warning(f"跳过不安全的扩展目录名: {ext_dir.name}")
                continue
            
            # 验证路径安全性（防止路径遍历）
            try:
                ext_dir.resolve().relative_to(self.extensions_dir.resolve())
            except ValueError:
                logger.warning(f"跳过不安全的扩展路径: {ext_dir}")
                continue
            
            if self._load_extension_from_directory(ext_dir):
                loaded_count += 1
        
        return loaded_count
    
    def _load_extension_from_directory(self, ext_dir: Path) -> bool:
        """从目录加载单个扩展"""
        try:
            # 验证目录路径安全性
            try:
                ext_dir.resolve().relative_to(self.extensions_dir.resolve())
            except ValueError:
                logger.error(f"不安全的扩展路径: {ext_dir}")
                return False

            # 查找扩展主文件
            main_file = ext_dir / "main.py"
            if not main_file.exists():
                logger.warning(f"扩展目录 {ext_dir.name} 缺少 main.py 文件")
                return False
            
            # 验证 main.py 文件路径安全性
            try:
                main_file.resolve().relative_to(ext_dir.resolve())
            except ValueError:
                logger.error(f"不安全的 main.py 路径: {main_file}")
                return False
            
            # 查找扩展配置文件
            config_file = ext_dir / "extension.json"
            extension_config = {}
            if config_file.exists():
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        extension_config = json.load(f)
                    # 验证配置文件内容
                    if not isinstance(extension_config, dict):
                        logger.warning(f"扩展配置文件格式无效: {ext_dir.name}")
                        extension_config = {}
                except json.JSONDecodeError as e:
                    logger.warning(f"扩展配置文件 JSON 解析失败: {ext_dir.name}, {str(e)}")
                    extension_config = {}
                except Exception as e:
                    logger.warning(f"读取扩展配置文件失败: {ext_dir.name}, {str(e)}")
                    extension_config = {}
            
            # 动态导入扩展模块
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                f"extension_{ext_dir.name}", main_file
            )
            module = importlib.util.module_from_spec(spec)
            
            # 添加当前目录到sys.path以支持相对导入
            import sys
            old_path = sys.path[:]
            sys.path.insert(0, str(ext_dir.parent.parent))
            
            try:
                spec.loader.exec_module(module)
            except Exception as e:
                logger.error(f"加载模块失败: {str(e)}")
                raise
            finally:
                sys.path[:] = old_path
            
            # 查找扩展类
            extension_classes = []
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, BaseExtension) and 
                    obj != BaseExtension and
                    obj.__module__ == module.__name__):  # 确保是在当前模块中定义的
                    extension_classes.append(obj)
            
            if not extension_classes:
                logger.warning(f"扩展目录 {ext_dir.name} 未找到有效的扩展类")
                return False

            
            # 注册所有找到的扩展类
            success_count = 0
            for extension_class in extension_classes:
                try:
                    # 创建扩展实例
                    user_config = self.extension_configs.get(ext_dir.name, {})
                    merged_config = {**extension_config, **user_config}
                    
                    extension = extension_class(merged_config)
                    
                    # 注册扩展
                    if self.registry.register_extension(extension):
                        success_count += 1
                except Exception as e:
                    logger.error(f"注册扩展类 {extension_class.__name__} 失败: {str(e)}")
            
            return success_count > 0
            
        except Exception as e:
            logger.error(f"加载扩展 {ext_dir.name} 失败: {str(e)}")
            return False
    
    def install_extension(self, extension_path: str, config: Dict[str, Any] = None) -> bool:
        """安装扩展"""
        try:
            from pathlib import Path
            import shutil
            import zipfile
            import tempfile
            import re
            
            config = config or {}
            extension_path_obj = Path(extension_path)
            
            # 验证扩展名称（从路径提取）
            def extract_extension_name(path: str) -> str:
                """从路径提取扩展名称"""
                # 从 URL 提取
                if path.startswith('http://') or path.startswith('https://') or path.startswith('git@'):
                    name = Path(path).stem.replace('.git', '')
                else:
                    name = Path(path).stem
                
                # 验证名称
                if not re.match(r'^[a-zA-Z0-9_-]+$', name):
                    raise ValueError(f"无效的扩展名称: {name}")
                
                return name
            
            # 如果是本地目录路径
            if extension_path_obj.exists() and extension_path_obj.is_dir():
                # 验证路径安全性
                try:
                    extension_path_obj.resolve().relative_to(Path.cwd().resolve())
                except ValueError:
                    # 路径不在当前工作目录下，需要额外验证
                    logger.warning(f"扩展路径不在当前工作目录: {extension_path}")
                
                # 复制扩展目录到 extensions 目录
                extension_name = extract_extension_name(extension_path)
                target_dir = self.extensions_dir / extension_name
                
                if target_dir.exists():
                    # 如果已存在，先删除
                    shutil.rmtree(target_dir)
                
                shutil.copytree(extension_path_obj, target_dir)
                
                # 保存配置
                if config:
                    self.extension_configs[extension_name] = config
                    self._save_extension_configs()
                
                # 重新加载扩展
                if self._load_extension_from_directory(target_dir):
                    logger.info(f"扩展 {extension_name} 安装成功")
                    return True
                else:
                    logger.error(f"扩展 {extension_name} 加载失败")
                    return False
            
            # 如果是 ZIP 文件路径
            elif extension_path_obj.exists() and extension_path_obj.suffix == '.zip':
                # 验证 ZIP 文件安全性
                try:
                    extension_path_obj.resolve().relative_to(Path.cwd().resolve())
                except ValueError:
                    logger.warning(f"ZIP 文件路径不在当前工作目录: {extension_path}")
                
                with zipfile.ZipFile(extension_path_obj, 'r') as zip_ref:
                    # 验证 ZIP 文件内容，防止 ZIP 炸弹攻击
                    total_size = sum(info.file_size for info in zip_ref.infolist())
                    if total_size > 100 * 1024 * 1024:  # 100MB 限制
                        raise ValueError("ZIP 文件过大，可能存在安全风险")
                    
                    # 检查是否有路径遍历攻击
                    for info in zip_ref.infolist():
                        if '..' in info.filename or info.filename.startswith('/'):
                            raise ValueError(f"ZIP 文件包含不安全的路径: {info.filename}")
                    
                    # 从 ZIP 文件名推断扩展名
                    extension_name = extract_extension_name(extension_path)
                    target_dir = self.extensions_dir / extension_name
                    
                    if target_dir.exists():
                        shutil.rmtree(target_dir)
                    
                    target_dir.mkdir(parents=True)
                    zip_ref.extractall(target_dir)
                
                # 保存配置
                if config:
                    self.extension_configs[extension_name] = config
                    self._save_extension_configs()
                
                # 重新加载扩展
                if self._load_extension_from_directory(target_dir):
                    logger.info(f"扩展 {extension_name} 安装成功")
                    return True
                else:
                    logger.error(f"扩展 {extension_name} 加载失败")
                    return False
            
            # 如果是 Git URL（需要 git 支持）
            elif extension_path.startswith('http://') or extension_path.startswith('https://') or extension_path.startswith('git@'):
                try:
                    import subprocess
                    import tempfile
                    import urllib.parse
                    
                    # 验证 URL 格式
                    if extension_path.startswith('http://') or extension_path.startswith('https://'):
                        parsed = urllib.parse.urlparse(extension_path)
                        if not parsed.netloc:
                            raise ValueError("无效的 Git URL")
                    
                    # 从 URL 推断扩展名
                    extension_name = extract_extension_name(extension_path)
                    target_dir = self.extensions_dir / extension_name
                    
                    if target_dir.exists():
                        shutil.rmtree(target_dir)
                    
                    # 克隆仓库到临时目录
                    with tempfile.TemporaryDirectory() as temp_dir:
                        temp_path = Path(temp_dir) / extension_name
                        subprocess.run(['git', 'clone', extension_path, str(temp_path)], 
                                     check=True, capture_output=True)
                        
                        # 移动到目标目录
                        shutil.move(str(temp_path), str(target_dir))
                    
                    # 保存配置
                    if config:
                        self.extension_configs[extension_name] = config
                        self._save_extension_configs()
                    
                    # 重新加载扩展
                    if self._load_extension_from_directory(target_dir):
                        logger.info(f"扩展 {extension_name} 安装成功")
                        return True
                    else:
                        logger.error(f"扩展 {extension_name} 加载失败")
                        return False
                        
                except subprocess.CalledProcessError as e:
                    logger.error(f"Git 克隆失败: {str(e)}")
                    return False
                except FileNotFoundError:
                    logger.error("Git 未安装，无法从 Git 仓库安装扩展")
                    return False
            else:
                logger.error(f"不支持的扩展路径格式: {extension_path}")
                return False
                
        except Exception as e:
            logger.error(f"安装扩展失败: {str(e)}")
            return False
    
    def uninstall_extension(self, name: str) -> bool:
        """卸载扩展"""
        try:
            import re
            import shutil
            
            # 验证扩展名称
            if not name or not isinstance(name, str):
                logger.error("扩展名称无效")
                return False
            
            # 防止路径遍历攻击
            if '..' in name or '/' in name or '\\' in name:
                logger.error(f"扩展名称包含非法字符: {name}")
                return False
            
            # 验证名称格式
            if not re.match(r'^[a-zA-Z0-9_-]+$', name):
                logger.error(f"扩展名称格式无效: {name}")
                return False
            
            # 检查扩展是否存在
            if name not in self.registry.extensions:
                logger.error(f"扩展不存在: {name}")
                return False
            
            # 注销扩展
            if not self.registry.unregister_extension(name):
                return False
            
            # 删除扩展目录（确保在 extensions_dir 内）
            ext_dir = self.extensions_dir / name
            try:
                # 验证路径安全性
                ext_dir.resolve().relative_to(self.extensions_dir.resolve())
            except ValueError:
                logger.error(f"不安全的扩展路径: {ext_dir}")
                return False
            
            if ext_dir.exists():
                shutil.rmtree(ext_dir)
            
            # 删除配置
            if name in self.extension_configs:
                del self.extension_configs[name]
                self._save_extension_configs()
            
            return True
            
        except Exception as e:
            logger.error(f"卸载扩展失败: {str(e)}")
            return False
    
    def configure_extension(self, name: str, config: Dict[str, Any]) -> bool:
        """配置扩展"""
        try:
            extension = self.registry.get_extension(name)
            if not extension:
                return False
            
            # 验证配置（如果扩展有验证方法）
            if hasattr(extension, 'validate_config'):
                if not extension.validate_config(config):
                    return False
            
            # 更新扩展实例的配置
            if hasattr(extension, 'config'):
                extension.config.update(config)
            
            # 保存到配置文件
            # 合并现有配置，保留 enabled 等状态
            current_config = self.extension_configs.get(name, {})
            current_config.update(config)
            self.extension_configs[name] = current_config
            self._save_extension_configs()
            
            return True
            
        except Exception as e:
            logger.error(f"配置扩展失败: {str(e)}")
            return False
    
    def get_extension_info(self, name: str) -> Optional[Dict[str, Any]]:
        """获取扩展信息"""
        extension = self.registry.get_extension(name)
        if not extension:
            return None
        
        metadata = extension.get_metadata()
        # 从配置中获取 enabled 状态，默认为 True
        extension_config = self.extension_configs.get(name, {})
        enabled = extension_config.get('enabled', True)
        
        # 构建返回数据
        result = metadata.to_dict()
        result.update({
            "config": extension.config,
            "enabled": enabled
        })
        # config_schema 已经在 metadata.to_dict() 中包含了
        
        return result
    
    def list_extensions(self) -> List[Dict[str, Any]]:
        """列出所有扩展"""
        extensions = []
        for extension in self.registry.extensions.values():
            metadata = extension.get_metadata()
            # 从配置中获取 enabled 状态，默认为 True
            extension_config = self.extension_configs.get(metadata.name, {})
            enabled = extension_config.get('enabled', True)
            
            # 构建返回数据
            result = metadata.to_dict()
            result.update({
                "config": extension.config,
                "enabled": enabled
            })
            # config_schema 已经在 metadata.to_dict() 中包含了
            
            extensions.append(result)
        return extensions
    
    def validate_product_with_extensions(self, product_type: str, product_data: Dict[str, Any], 
                                       files: Dict[str, bytes]) -> tuple[bool, List[str]]:
        """使用扩展验证产品"""
        errors = []
        
        # 使用产品类型扩展验证
        type_extension = self.registry.get_product_type_extension(product_type)
        if type_extension:
            is_valid, error_msg = type_extension.validate_product_files(files)
            if not is_valid:
                errors.append(error_msg)
        
        # 使用验证器扩展
        for validator in self.registry.validators.values():
            try:
                is_valid, validator_errors = validator.validate_product(product_data, files)
                if not is_valid:
                    errors.extend(validator_errors)
            except Exception as e:
                errors.append(f"验证器 {validator.get_metadata().name} 执行失败: {str(e)}")
        
        return len(errors) == 0, errors
    
    def process_product_with_extensions(self, product_type: str, product_data: Dict[str, Any], 
                                      files: Dict[str, bytes]) -> tuple[Dict[str, Any], Dict[str, bytes]]:
        """使用扩展处理产品"""
        result_data = product_data.copy()
        result_files = files.copy()
        
        # 使用产品类型扩展处理
        type_extension = self.registry.get_product_type_extension(product_type)
        if type_extension:
            result_files = type_extension.process_product_files(result_files)
        
        # 使用处理器扩展
        for processor in self.registry.processors.values():
            try:
                result_data, result_files = processor.process_product(result_data, result_files)
            except Exception as e:
                logger.error(f"处理器 {processor.get_metadata().name} 执行失败: {str(e)}")
        
        return result_data, result_files
    
    def render_product_with_extensions(self, product_id: int, product_type: str, 
                                     config: Dict[str, Any]) -> Optional[str]:
        """使用扩展渲染产品"""
        # 查找对应的渲染器
        type_extension = self.registry.get_product_type_extension(product_type)
        if type_extension:
            type_def = type_extension.get_product_type_definition()
            if type_def.renderer_class:
                renderer = self.registry.renderers.get(type_def.renderer_class)
                if renderer:
                    try:
                        return renderer.render_product(product_id, config)
                    except Exception as e:
                        logger.error(f"渲染器 {type_def.renderer_class} 执行失败: {str(e)}")
        
        return None
    
    def execute_hooks(self, hook_type: HookType, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行钩子"""
        return self.registry.execute_hooks(hook_type, context)
    
    def process_middlewares(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理中间件"""
        return self.registry.process_middlewares(request_data)
    
    def get_available_product_types(self) -> List[Dict[str, Any]]:
        """获取可用的产品类型"""
        types = []
        for type_def in self.registry.get_available_product_types():
            types.append(type_def.to_dict())
        return types


# 全局扩展服务实例
product_extension_service = ProductExtensionService()


# 内置扩展示例

class StaticWebExtension(ProductTypeExtension):
    """静态Web应用扩展"""
    
    def get_metadata(self) -> ExtensionMetadata:
        return ExtensionMetadata(
            name="static_web",
            version="1.0.0",
            description="静态Web应用支持",
            author="System",
            extension_type=ExtensionType.PRODUCT_TYPE,
            dependencies=[],
            config_schema={}
        )
    
    def get_product_type_definition(self) -> ProductTypeDefinition:
        return ProductTypeDefinition(
            type_name="static",
            display_name="静态Web应用",
            description="支持HTML、CSS、JavaScript的静态网站",
            file_extensions=[".html", ".htm", ".css", ".js", ".json", ".txt"],
            entry_files=["index.html", "main.html", "app.html"],
            config_schema={
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "theme": {"type": "string", "enum": ["light", "dark"]},
                    "responsive": {"type": "boolean", "default": True}
                }
            }
        )
    
    def validate_product_files(self, files: Dict[str, bytes]) -> tuple[bool, str]:
        # 检查是否包含HTML入口文件
        html_files = [f for f in files.keys() if f.endswith(('.html', '.htm'))]
        if not html_files:
            return False, "静态Web应用必须包含至少一个HTML文件"
        
        return True, ""


class SPAExtension(ProductTypeExtension):
    """单页应用扩展"""
    
    def get_metadata(self) -> ExtensionMetadata:
        return ExtensionMetadata(
            name="spa",
            version="1.0.0",
            description="单页应用支持",
            author="System",
            extension_type=ExtensionType.PRODUCT_TYPE,
            dependencies=[],
            config_schema={}
        )
    
    def get_product_type_definition(self) -> ProductTypeDefinition:
        return ProductTypeDefinition(
            type_name="spa",
            display_name="单页应用",
            description="支持React、Vue、Angular等SPA框架",
            file_extensions=[".html", ".js", ".css", ".json", ".map"],
            entry_files=["index.html"],
            config_schema={
                "type": "object",
                "properties": {
                    "framework": {"type": "string", "enum": ["react", "vue", "angular", "other"]},
                    "router_mode": {"type": "string", "enum": ["hash", "history"]},
                    "base_url": {"type": "string", "default": "/"}
                }
            }
        )
    
    def validate_product_files(self, files: Dict[str, bytes]) -> tuple[bool, str]:
        # 检查是否包含index.html
        if "index.html" not in files:
            return False, "SPA应用必须包含index.html文件"
        
        return True, ""


# 注册内置扩展
def register_builtin_extensions():
    """注册内置扩展"""
    product_extension_service.registry.register_extension(StaticWebExtension())
    product_extension_service.registry.register_extension(SPAExtension())


# 初始化时注册内置扩展
register_builtin_extensions()