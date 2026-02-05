"""
产品文件存储服务
负责产品文件的上传、存储、验证和管理
扩展功能：文件上传下载、资源管理、版本控制、安全扫描
"""

import os
import shutil
import zipfile
import tempfile
import hashlib
import mimetypes
import json
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Union, BinaryIO
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
from enum import Enum

from ..models import Product as ProductModel
from ..schemas import ProductUploadResponse


class FileType(Enum):
    """文件类型枚举"""
    HTML = "html"
    CSS = "css"
    JAVASCRIPT = "javascript"
    IMAGE = "image"
    FONT = "font"
    AUDIO = "audio"
    VIDEO = "video"
    DATA = "data"
    UNKNOWN = "unknown"


@dataclass
class FileVersion:
    """文件版本信息"""
    version: str
    timestamp: datetime
    file_hash: str
    size: int
    description: Optional[str] = None
    
    def to_dict(self):
        return {
            **asdict(self),
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class SecurityScanResult:
    """安全扫描结果"""
    is_safe: bool
    threats: List[str]
    warnings: List[str]
    scan_time: datetime
    
    def to_dict(self):
        return {
            **asdict(self),
            'scan_time': self.scan_time.isoformat()
        }


class ProductFileService:
    """产品文件存储服务 - 扩展版本"""
    
    def __init__(self, base_dir: str = None):
        # 默认使用 backend/products 目录
        if base_dir is None:
            # 从当前文件位置计算 backend/products 路径
            current_file = Path(__file__)
            backend_dir = current_file.parent.parent.parent  # 从 app/services/product_file_service.py 到 backend
            base_dir = str(backend_dir / "products")
        
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建子目录
        self.versions_dir = self.base_dir / "versions"
        self.backups_dir = self.base_dir / "backups"
        self.temp_dir = self.base_dir / "temp"
        
        for dir_path in [self.versions_dir, self.backups_dir, self.temp_dir]:
            dir_path.mkdir(exist_ok=True)
        
        # 文件安全配置
        self.max_file_size = 100 * 1024 * 1024  # 100MB
        self.max_total_size = 500 * 1024 * 1024  # 500MB per product
        self.allowed_extensions = {'.zip'}
        self.allowed_mime_types = {'application/zip', 'application/x-zip-compressed'}
        
        # 危险文件扩展名黑名单（服务器端可执行文件）
        self.dangerous_extensions = {
            '.exe', '.bat', '.cmd', '.com', '.pif', '.scr', '.vbs',
            '.jar', '.php', '.asp', '.aspx', '.jsp', '.py', '.rb', '.pl',
            '.sh', '.ps1', '.dll', '.so', '.dylib'
        }
        
        # 允许的产品文件扩展名
        self.safe_extensions = {
            '.html', '.htm', '.css', '.js', '.json', '.txt', '.md',
            '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.webp',
            '.mp3', '.wav', '.ogg', '.mp4', '.webm', '.avi', '.mov',
            '.woff', '.woff2', '.ttf', '.eot', '.otf',
            '.xml', '.csv', '.pdf', '.map', '.yaml', '.yml'
        }
        
        # 文件类型映射
        self.file_type_mapping = {
            '.html': FileType.HTML, '.htm': FileType.HTML,
            '.css': FileType.CSS,
            '.js': FileType.JAVASCRIPT, '.mjs': FileType.JAVASCRIPT,
            '.png': FileType.IMAGE, '.jpg': FileType.IMAGE, '.jpeg': FileType.IMAGE,
            '.gif': FileType.IMAGE, '.svg': FileType.IMAGE, '.ico': FileType.IMAGE,
            '.webp': FileType.IMAGE,
            '.woff': FileType.FONT, '.woff2': FileType.FONT, '.ttf': FileType.FONT,
            '.eot': FileType.FONT, '.otf': FileType.FONT,
            '.mp3': FileType.AUDIO, '.wav': FileType.AUDIO, '.ogg': FileType.AUDIO,
            '.mp4': FileType.VIDEO, '.webm': FileType.VIDEO, '.avi': FileType.VIDEO,
            '.mov': FileType.VIDEO,
            '.json': FileType.DATA, '.xml': FileType.DATA, '.csv': FileType.DATA,
            '.yaml': FileType.DATA, '.yml': FileType.DATA
        }
        
        # 恶意代码模式
        self.malicious_patterns = [
            # JavaScript恶意模式
            r'eval\s*\(',
            r'Function\s*\(',
            r'document\.write\s*\(',
            r'innerHTML\s*=',
            r'outerHTML\s*=',
            r'<script[^>]*>.*?</script>',
            r'javascript\s*:',
            r'on\w+\s*=',
            
            # HTML恶意模式
            r'<iframe[^>]*>',
            r'<object[^>]*>',
            r'<embed[^>]*>',
            r'<form[^>]*action\s*=\s*["\']?https?://',
            
            # CSS恶意模式
            r'@import\s+url\s*\(',
            r'expression\s*\(',
            r'behavior\s*:',
            
            # 通用恶意模式
            r'base64\s*,\s*[A-Za-z0-9+/=]{100,}',  # 长base64字符串
            r'\\x[0-9a-fA-F]{2}',  # 十六进制编码
            r'%[0-9a-fA-F]{2}',    # URL编码
        ]
    
    def validate_zip_file(self, file_path: str) -> Tuple[bool, str, List[str]]:
        """
        验证ZIP文件的安全性和完整性
        
        Returns:
            (is_valid, error_message, file_list)
        """
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                file_list = zip_ref.namelist()
                
                # 检查文件数量限制
                if len(file_list) > 1000:
                    return False, "ZIP文件包含过多文件（超过1000个）", []
                
                # 检查文件路径安全性
                for file_name in file_list:
                    # 检查路径遍历攻击
                    if '..' in file_name or file_name.startswith('/'):
                        return False, f"检测到不安全的文件路径: {file_name}", []
                    
                    # 检查文件扩展名
                    file_ext = Path(file_name).suffix.lower()
                    if file_ext in self.dangerous_extensions:
                        return False, f"包含危险文件类型: {file_name}", []
                    
                    # 检查文件名长度
                    if len(file_name) > 255:
                        return False, f"文件名过长: {file_name}", []
                
                # 检查ZIP文件完整性
                bad_file = zip_ref.testzip()
                if bad_file:
                    return False, f"ZIP文件损坏: {bad_file}", []
                
                return True, "", file_list
                
        except zipfile.BadZipFile:
            return False, "无效的ZIP文件格式", []
        except Exception as e:
            return False, f"ZIP文件验证失败: {str(e)}", []
    
    def calculate_file_hash(self, file_path: str) -> str:
        """计算文件SHA256哈希值"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    def extract_zip_safely(self, zip_path: str, extract_to: str) -> List[str]:
        """
        安全地解压ZIP文件
        
        Returns:
            解压的文件列表
        """
        extracted_files = []
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for member in zip_ref.infolist():
                # 再次验证文件路径安全性
                if '..' in member.filename or member.filename.startswith('/'):
                    continue
                
                # 创建安全的文件路径（使用跨平台路径）
                extract_to_path = Path(extract_to)
                safe_path = extract_to_path / member.filename
                safe_path = safe_path.resolve()
                
                # 确保路径在目标目录内
                try:
                    safe_path.relative_to(extract_to_path.resolve())
                except ValueError:
                    continue
                
                # 创建目录
                if member.is_dir():
                    safe_path.mkdir(parents=True, exist_ok=True)
                else:
                    # 确保父目录存在
                    safe_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # 解压文件
                    with zip_ref.open(member) as source, open(safe_path, 'wb') as target:
                        shutil.copyfileobj(source, target)
                    
                    extracted_files.append(member.filename)
        
        return extracted_files
    
    def get_product_directory(self, product_id: int) -> Path:
        """
        获取产品存储目录路径（基于ID，固定路径结构）
        
        Args:
            product_id: 产品ID
        
        Returns:
            产品目录路径
        """
        return self.base_dir / str(product_id)
    
    def create_product_directory(self, product_id: int) -> Path:
        """
        为产品创建存储目录（如果已存在则先清理）
        
        Args:
            product_id: 产品ID
        
        Returns:
            产品目录路径
        """
        product_dir = self.get_product_directory(product_id)
        
        # 如果目录已存在，先清理
        if product_dir.exists():
            shutil.rmtree(product_dir, ignore_errors=True)
        
        product_dir.mkdir(parents=True, exist_ok=True)
        return product_dir.absolute()
    
    def upload_product_files(self, product: ProductModel, file_path: str) -> ProductUploadResponse:
        """
        上传并处理产品文件
        
        Args:
            product: 产品模型实例
            file_path: 上传的ZIP文件路径
        
        Returns:
            ProductUploadResponse
        """
        try:
            # 验证ZIP文件
            is_valid, error_msg, file_list = self.validate_zip_file(file_path)
            if not is_valid:
                raise ValueError(error_msg)
            
            # 检查是否包含入口文件
            entry_file_found = any(
                f.endswith(product.entry_file) for f in file_list
            )
            if not entry_file_found:
                raise ValueError(f"ZIP文件中未找到入口文件: {product.entry_file}")
            
            # 创建产品目录
            product_dir = self.create_product_directory(product.id)
            
            try:
                # 安全解压文件
                extracted_files = self.extract_zip_safely(file_path, str(product_dir))
                
                # 验证入口文件是否存在
                entry_file_path = product_dir / product.entry_file
                if not entry_file_path.exists():
                    # 尝试查找入口文件（可能路径不同）
                    entry_found = False
                    for extracted_file in extracted_files:
                        if Path(extracted_file).name == product.entry_file:
                            entry_found = True
                            # 移动文件到正确位置
                            extracted_path = product_dir / extracted_file
                            if extracted_path.exists():
                                shutil.move(str(extracted_path), str(entry_file_path))
                            break
                    
                    if not entry_found:
                        raise ValueError(f"解压后未找到入口文件: {product.entry_file}")
                
                # 计算文件哈希（用于完整性验证）
                file_hash = self.calculate_file_hash(file_path)
                
                # 创建元数据文件
                metadata = {
                    "product_id": product.id,
                    "upload_time": datetime.now(timezone.utc).isoformat(),
                    "file_hash": file_hash,
                    "extracted_files": extracted_files,
                    "entry_file": product.entry_file
                }
                
                metadata_path = product_dir / ".metadata.json"
                import json
                with open(metadata_path, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2, ensure_ascii=False)
                
                # 生成基于ID的文件路径标记（用于前端判断文件是否已上传）
                # 实际文件路径基于ID计算，但需要设置标记值以便前端识别
                file_path_marker = f"/products/{product.id}/"
                
                # 返回上传结果
                return ProductUploadResponse(
                    message="产品文件上传成功",
                    product_id=product.id,
                    file_path=file_path_marker,  # 设置标记值，用于前端判断文件已上传
                    extracted_files=extracted_files
                )
                
            except Exception as e:
                # 清理失败的上传
                if product_dir.exists():
                    shutil.rmtree(product_dir, ignore_errors=True)
                raise ValueError(f"文件处理失败: {str(e)}")
                
        except Exception as e:
            raise ValueError(f"文件上传失败: {str(e)}")
    
    def get_product_files(self, product_id: int) -> Dict:
        """获取产品文件信息（基于ID的固定路径）"""
        product_dir = self.get_product_directory(product_id)
        
        if not product_dir.exists():
            return {"files": [], "message": "产品文件不存在"}
        
        files = []
        for file_path in product_dir.rglob('*'):
            if file_path.is_file() and not file_path.name.startswith('.'):
                relative_path = file_path.relative_to(product_dir)
                stat = file_path.stat()
                
                files.append({
                    "name": file_path.name,
                    "path": str(relative_path),
                    "size": stat.st_size,
                    "modified": stat.st_mtime,
                    "type": mimetypes.guess_type(str(file_path))[0] or "unknown"
                })
        
        # 读取元数据
        metadata_path = product_dir / ".metadata.json"
        metadata = {}
        if metadata_path.exists():
            try:
                import json
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
            except:
                pass
        
        return {
            "files": files,
            "metadata": metadata,
            "total_files": len(files),
            "total_size": sum(f["size"] for f in files)
        }
    
    def delete_product_files(self, product_id: int) -> bool:
        """删除产品文件（基于ID的固定路径）"""
        product_dir = self.get_product_directory(product_id)
        
        if product_dir.exists():
            try:
                shutil.rmtree(product_dir)
                return True
            except Exception as e:
                print(f"删除产品文件失败: {e}")
                return False
        
        return True
    
    def verify_product_integrity(self, product_id: int) -> Tuple[bool, str]:
        """验证产品文件完整性（基于ID的固定路径）"""
        product_dir = self.get_product_directory(product_id)
        
        if not product_dir.exists():
            return False, "产品目录不存在"
        
        # 读取元数据
        metadata_path = product_dir / ".metadata.json"
        if not metadata_path.exists():
            return False, "缺少元数据文件"
        
        try:
            import json
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # 验证文件是否存在
            expected_files = metadata.get("extracted_files", [])
            missing_files = []
            for file_name in expected_files:
                file_path = product_dir / file_name
                if not file_path.exists():
                    missing_files.append(file_name)
            
            if missing_files:
                return False, f"缺少文件: {', '.join(missing_files)}"
            
            # 验证入口文件
            entry_file = metadata.get("entry_file")
            if entry_file:
                entry_path = product_dir / entry_file
                if not entry_path.exists():
                    return False, f"缺少入口文件: {entry_file}"
            
            return True, "文件完整性验证通过"
            
        except json.JSONDecodeError as e:
            return False, f"元数据文件格式错误: {str(e)}"
        except Exception as e:
            return False, f"验证失败: {str(e)}"
    
    def get_storage_stats(self) -> Dict:
        """获取存储统计信息"""
        if not self.base_dir.exists():
            return {
                "total_products": 0,
                "total_size": 0,
                "total_files": 0
            }
        
        total_size = 0
        total_files = 0
        product_count = 0
        
        for product_dir in self.base_dir.iterdir():
            if product_dir.is_dir() and product_dir.name.isdigit():
                product_count += 1
                for file_path in product_dir.rglob('*'):
                    if file_path.is_file():
                        total_files += 1
                        total_size += file_path.stat().st_size
        
        return {
            "total_products": product_count,
            "total_size": total_size,
            "total_files": total_files,
            "storage_path": str(self.base_dir)
        }
    
    # ==================== 扩展功能：文件上传下载 ====================
    
    def upload_individual_file(self, product_id: int, file_name: str, file_content: Union[bytes, BinaryIO], 
                             description: str = None) -> Dict:
        """
        上传单个文件到产品目录
        
        Args:
            product_id: 产品ID
            file_name: 文件名
            file_content: 文件内容（字节或文件对象）
            description: 文件描述
        
        Returns:
            上传结果信息
        """
        # 验证文件名安全性
        if not self._is_safe_filename(file_name):
            raise ValueError(f"不安全的文件名: {file_name}")
        
        # 检查文件扩展名
        file_ext = Path(file_name).suffix.lower()
        if file_ext not in self.safe_extensions:
            raise ValueError(f"不支持的文件类型: {file_ext}")
        
        product_dir = self.get_product_directory(product_id)
        if not product_dir.exists():
            raise ValueError(f"产品目录不存在: {product_id}")
        
        file_path = product_dir / file_name
        
        # 确保父目录存在
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 写入文件
        if isinstance(file_content, bytes):
            content = file_content
        else:
            content = file_content.read()
        
        # 检查文件大小
        if len(content) > self.max_file_size:
            raise ValueError(f"文件大小超过限制: {len(content)} > {self.max_file_size}")
        
        # 安全扫描
        scan_result = self.scan_file_content(content, file_name)
        if not scan_result.is_safe:
            raise ValueError(f"文件安全扫描失败: {', '.join(scan_result.threats)}")
        
        # 写入文件
        with open(file_path, 'wb') as f:
            f.write(content)
        
        # 计算文件哈希
        file_hash = hashlib.sha256(content).hexdigest()
        
        # 更新文件记录
        self._update_file_record(product_id, file_name, file_hash, len(content), description)
        
        return {
            "message": "文件上传成功",
            "file_name": file_name,
            "file_size": len(content),
            "file_hash": file_hash,
            "file_type": self._get_file_type(file_name).value,
            "scan_result": scan_result.to_dict()
        }
    
    def download_file(self, product_id: int, file_path: str) -> Tuple[bytes, str, str]:
        """
        下载产品文件
        
        Args:
            product_id: 产品ID
            file_path: 文件相对路径
        
        Returns:
            (文件内容, 文件名, MIME类型)
        """
        # 验证路径安全性
        if not self._is_safe_path(file_path):
            raise ValueError(f"不安全的文件路径: {file_path}")
        
        product_dir = self.get_product_directory(product_id)
        full_path = product_dir / file_path
        
        # 确保文件在产品目录内
        try:
            full_path.resolve().relative_to(product_dir.resolve())
        except ValueError:
            raise ValueError("文件路径超出产品目录范围")
        
        if not full_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        if not full_path.is_file():
            raise ValueError(f"路径不是文件: {file_path}")
        
        # 读取文件
        with open(full_path, 'rb') as f:
            content = f.read()
        
        # 获取MIME类型
        mime_type, _ = mimetypes.guess_type(str(full_path))
        if not mime_type:
            mime_type = 'application/octet-stream'
        
        return content, full_path.name, mime_type
    
    def delete_file(self, product_id: int, file_path: str) -> Dict:
        """
        删除产品文件
        
        Args:
            product_id: 产品ID
            file_path: 文件相对路径
        
        Returns:
            删除结果信息
        """
        # 验证路径安全性
        if not self._is_safe_path(file_path):
            raise ValueError(f"不安全的文件路径: {file_path}")
        
        product_dir = self.get_product_directory(product_id)
        full_path = product_dir / file_path
        
        # 确保文件在产品目录内
        try:
            full_path.resolve().relative_to(product_dir.resolve())
        except ValueError:
            raise ValueError("文件路径超出产品目录范围")
        
        if not full_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        # 备份文件（如果需要）
        backup_path = self._create_file_backup(product_id, file_path)
        
        # 删除文件
        if full_path.is_file():
            full_path.unlink()
        elif full_path.is_dir():
            shutil.rmtree(full_path)
        
        # 更新文件记录
        self._remove_file_record(product_id, file_path)
        
        return {
            "message": "文件删除成功",
            "deleted_path": file_path,
            "backup_path": str(backup_path) if backup_path else None
        }
    
    # ==================== 扩展功能：版本控制 ====================
    
    def create_version(self, product_id: int, version: str, description: str = None) -> Dict:
        """
        创建产品版本快照
        
        Args:
            product_id: 产品ID
            version: 版本号
            description: 版本描述
        
        Returns:
            版本创建结果
        """
        product_dir = self.get_product_directory(product_id)
        if not product_dir.exists():
            raise ValueError(f"产品目录不存在: {product_id}")
        
        # 创建版本目录
        version_dir = self.versions_dir / str(product_id) / version
        version_dir.mkdir(parents=True, exist_ok=True)
        
        # 复制产品文件
        copied_files = []
        total_size = 0
        
        for file_path in product_dir.rglob('*'):
            if file_path.is_file() and not file_path.name.startswith('.'):
                relative_path = file_path.relative_to(product_dir)
                target_path = version_dir / relative_path
                
                # 创建目标目录
                target_path.parent.mkdir(parents=True, exist_ok=True)
                
                # 复制文件
                shutil.copy2(file_path, target_path)
                copied_files.append(str(relative_path))
                total_size += file_path.stat().st_size
        
        # 创建版本信息
        version_info = FileVersion(
            version=version,
            timestamp=datetime.now(timezone.utc),
            file_hash=self._calculate_directory_hash(product_dir),
            size=total_size,
            description=description
        )
        
        # 保存版本元数据
        version_metadata_path = version_dir / ".version.json"
        with open(version_metadata_path, 'w', encoding='utf-8') as f:
            json.dump({
                **version_info.to_dict(),
                "files": copied_files,
                "product_id": product_id
            }, f, indent=2, ensure_ascii=False)
        
        # 更新版本历史
        self._update_version_history(product_id, version_info)
        
        return {
            "message": "版本创建成功",
            "version": version,
            "files_count": len(copied_files),
            "total_size": total_size,
            "version_path": str(version_dir)
        }
    
    def list_versions(self, product_id: int) -> List[Dict]:
        """
        列出产品的所有版本
        
        Args:
            product_id: 产品ID
        
        Returns:
            版本列表
        """
        versions_path = self.versions_dir / str(product_id)
        if not versions_path.exists():
            return []
        
        versions = []
        for version_dir in versions_path.iterdir():
            if version_dir.is_dir():
                version_metadata_path = version_dir / ".version.json"
                if version_metadata_path.exists():
                    try:
                        with open(version_metadata_path, 'r', encoding='utf-8') as f:
                            version_data = json.load(f)
                        versions.append(version_data)
                    except:
                        continue
        
        # 按时间戳排序
        versions.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return versions
    
    def restore_version(self, product_id: int, version: str) -> Dict:
        """
        恢复到指定版本
        
        Args:
            product_id: 产品ID
            version: 版本号
        
        Returns:
            恢复结果
        """
        version_dir = self.versions_dir / str(product_id) / version
        if not version_dir.exists():
            raise ValueError(f"版本不存在: {version}")
        
        product_dir = self.get_product_directory(product_id)
        
        # 备份当前版本
        backup_version = f"backup_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
        self.create_version(product_id, backup_version, "自动备份（版本恢复前）")
        
        # 清空当前产品目录
        if product_dir.exists():
            for item in product_dir.iterdir():
                if not item.name.startswith('.'):
                    if item.is_file():
                        item.unlink()
                    else:
                        shutil.rmtree(item)
        else:
            product_dir.mkdir(parents=True, exist_ok=True)
        
        # 恢复版本文件
        restored_files = []
        for file_path in version_dir.rglob('*'):
            if file_path.is_file() and not file_path.name.startswith('.'):
                relative_path = file_path.relative_to(version_dir)
                target_path = product_dir / relative_path
                
                # 创建目标目录
                target_path.parent.mkdir(parents=True, exist_ok=True)
                
                # 复制文件
                shutil.copy2(file_path, target_path)
                restored_files.append(str(relative_path))
        
        return {
            "message": "版本恢复成功",
            "restored_version": version,
            "backup_version": backup_version,
            "restored_files": len(restored_files)
        }
    
    def delete_version(self, product_id: int, version: str) -> Dict:
        """
        删除指定版本
        
        Args:
            product_id: 产品ID
            version: 版本号
        
        Returns:
            删除结果
        """
        version_dir = self.versions_dir / str(product_id) / version
        if not version_dir.exists():
            raise ValueError(f"版本不存在: {version}")
        
        # 删除版本目录
        shutil.rmtree(version_dir)
        
        # 更新版本历史
        self._remove_version_from_history(product_id, version)
        
        return {
            "message": "版本删除成功",
            "deleted_version": version
        }
    
    # ==================== 扩展功能：安全扫描 ====================
    
    def scan_file_content(self, content: bytes, filename: str) -> SecurityScanResult:
        """
        扫描文件内容的安全性
        
        Args:
            content: 文件内容
            filename: 文件名
        
        Returns:
            安全扫描结果
        """
        threats = []
        warnings = []
        
        try:
            # 尝试解码为文本进行内容扫描
            text_content = content.decode('utf-8', errors='ignore')
            
            # 检查恶意代码模式
            for pattern in self.malicious_patterns:
                if re.search(pattern, text_content, re.IGNORECASE | re.DOTALL):
                    threats.append(f"检测到可疑代码模式: {pattern[:50]}...")
            
            # 检查文件大小
            if len(content) > self.max_file_size:
                threats.append(f"文件大小超过限制: {len(content)} > {self.max_file_size}")
            
            # 检查文件类型特定的安全问题
            file_ext = Path(filename).suffix.lower()
            
            if file_ext in ['.html', '.htm']:
                self._scan_html_content(text_content, threats, warnings)
            elif file_ext == '.js':
                self._scan_javascript_content(text_content, threats, warnings)
            elif file_ext == '.css':
                self._scan_css_content(text_content, threats, warnings)
            
            # 检查二进制内容
            self._scan_binary_content(content, threats, warnings)
            
        except Exception as e:
            warnings.append(f"扫描过程中出现错误: {str(e)}")
        
        return SecurityScanResult(
            is_safe=len(threats) == 0,
            threats=threats,
            warnings=warnings,
            scan_time=datetime.now(timezone.utc)
        )
    
    def scan_product_files(self, product_id: int) -> Dict:
        """
        扫描产品所有文件的安全性
        
        Args:
            product_id: 产品ID
        
        Returns:
            扫描结果汇总
        """
        product_dir = self.get_product_directory(product_id)
        if not product_dir.exists():
            raise ValueError(f"产品目录不存在: {product_id}")
        
        scan_results = []
        total_threats = 0
        total_warnings = 0
        
        for file_path in product_dir.rglob('*'):
            if file_path.is_file() and not file_path.name.startswith('.'):
                try:
                    with open(file_path, 'rb') as f:
                        content = f.read()
                    
                    relative_path = file_path.relative_to(product_dir)
                    scan_result = self.scan_file_content(content, file_path.name)
                    
                    scan_results.append({
                        "file_path": str(relative_path),
                        "is_safe": scan_result.is_safe,
                        "threats": scan_result.threats,
                        "warnings": scan_result.warnings,
                        "scan_time": scan_result.scan_time.isoformat()
                    })
                    
                    total_threats += len(scan_result.threats)
                    total_warnings += len(scan_result.warnings)
                    
                except Exception as e:
                    scan_results.append({
                        "file_path": str(relative_path),
                        "is_safe": False,
                        "threats": [f"扫描失败: {str(e)}"],
                        "warnings": [],
                        "scan_time": datetime.now(timezone.utc).isoformat()
                    })
                    total_threats += 1
        
        return {
            "product_id": product_id,
            "scan_time": datetime.now(timezone.utc).isoformat(),
            "total_files": len(scan_results),
            "safe_files": len([r for r in scan_results if r["is_safe"]]),
            "total_threats": total_threats,
            "total_warnings": total_warnings,
            "is_safe": total_threats == 0,
            "files": scan_results
        }
    
    # ==================== 私有辅助方法 ====================
    
    def _is_safe_filename(self, filename: str) -> bool:
        """检查文件名是否安全"""
        # 检查路径遍历
        if '..' in filename or filename.startswith('/') or '\\' in filename:
            return False
        
        # 检查文件名长度
        if len(filename) > 255:
            return False
        
        # 检查特殊字符
        dangerous_chars = ['<', '>', ':', '"', '|', '?', '*', '\0']
        if any(char in filename for char in dangerous_chars):
            return False
        
        return True
    
    def _is_safe_path(self, path: str) -> bool:
        """检查路径是否安全"""
        # 检查路径遍历
        if '..' in path or path.startswith('/') or path.startswith('\\'):
            return False
        
        # 检查路径长度
        if len(path) > 500:
            return False
        
        return True
    
    def _get_file_type(self, filename: str) -> FileType:
        """获取文件类型"""
        ext = Path(filename).suffix.lower()
        return self.file_type_mapping.get(ext, FileType.UNKNOWN)
    
    def _update_file_record(self, product_id: int, filename: str, file_hash: str, 
                          size: int, description: str = None):
        """更新文件记录（基于ID的固定路径）"""
        product_dir = self.get_product_directory(product_id)
        records_path = product_dir / ".file_records.json"
        
        # 读取现有记录
        records = {}
        if records_path.exists():
            try:
                with open(records_path, 'r', encoding='utf-8') as f:
                    records = json.load(f)
            except:
                pass
        
        # 更新记录
        records[filename] = {
            "hash": file_hash,
            "size": size,
            "type": self._get_file_type(filename).value,
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "description": description
        }
        
        # 保存记录
        with open(records_path, 'w', encoding='utf-8') as f:
            json.dump(records, f, indent=2, ensure_ascii=False)
    
    def _remove_file_record(self, product_id: int, filename: str):
        """移除文件记录（基于ID的固定路径）"""
        product_dir = self.get_product_directory(product_id)
        records_path = product_dir / ".file_records.json"
        
        if records_path.exists():
            try:
                with open(records_path, 'r', encoding='utf-8') as f:
                    records = json.load(f)
                
                if filename in records:
                    del records[filename]
                    
                    with open(records_path, 'w', encoding='utf-8') as f:
                        json.dump(records, f, indent=2, ensure_ascii=False)
            except:
                pass
    
    def _create_file_backup(self, product_id: int, file_path: str) -> Optional[Path]:
        """创建文件备份（基于ID的固定路径）"""
        try:
            product_dir = self.get_product_directory(product_id)
            source_path = product_dir / file_path
            
            if not source_path.exists():
                return None
            
            # 创建备份目录
            backup_dir = self.backups_dir / str(product_id)
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # 生成备份文件名
            timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
            backup_filename = f"{Path(file_path).stem}_{timestamp}{Path(file_path).suffix}"
            backup_path = backup_dir / backup_filename
            
            # 复制文件
            shutil.copy2(source_path, backup_path)
            return backup_path
            
        except Exception:
            return None
    
    def _calculate_directory_hash(self, directory: Path) -> str:
        """计算目录的哈希值"""
        hash_sha256 = hashlib.sha256()
        
        for file_path in sorted(directory.rglob('*')):
            if file_path.is_file() and not file_path.name.startswith('.'):
                # 添加文件路径到哈希
                relative_path = file_path.relative_to(directory)
                hash_sha256.update(str(relative_path).encode('utf-8'))
                
                # 添加文件内容到哈希
                with open(file_path, 'rb') as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        hash_sha256.update(chunk)
        
        return hash_sha256.hexdigest()
    
    def _update_version_history(self, product_id: int, version_info: FileVersion):
        """更新版本历史"""
        history_path = self.versions_dir / str(product_id) / ".history.json"
        
        # 读取现有历史
        history = []
        if history_path.exists():
            try:
                with open(history_path, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            except:
                pass
        
        # 添加新版本
        history.append(version_info.to_dict())
        
        # 保存历史
        history_path.parent.mkdir(parents=True, exist_ok=True)
        with open(history_path, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
    
    def _remove_version_from_history(self, product_id: int, version: str):
        """从版本历史中移除版本"""
        history_path = self.versions_dir / str(product_id) / ".history.json"
        
        if history_path.exists():
            try:
                with open(history_path, 'r', encoding='utf-8') as f:
                    history = json.load(f)
                
                # 移除指定版本
                history = [v for v in history if v.get('version') != version]
                
                with open(history_path, 'w', encoding='utf-8') as f:
                    json.dump(history, f, indent=2, ensure_ascii=False)
            except:
                pass
    
    def _scan_html_content(self, content: str, threats: List[str], warnings: List[str]):
        """扫描HTML内容"""
        # 检查内联脚本
        if re.search(r'<script[^>]*>(?!.*src=)', content, re.IGNORECASE):
            warnings.append("包含内联JavaScript代码")
        
        # 检查外部资源
        external_resources = re.findall(r'(?:src|href)=["\']?(https?://[^"\'>\s]+)', content, re.IGNORECASE)
        if external_resources:
            warnings.append(f"包含外部资源引用: {len(external_resources)}个")
        
        # 检查表单提交
        if re.search(r'<form[^>]*action\s*=\s*["\']?https?://', content, re.IGNORECASE):
            threats.append("包含向外部URL提交的表单")
    
    def _scan_javascript_content(self, content: str, threats: List[str], warnings: List[str]):
        """扫描JavaScript内容"""
        # 检查动态代码执行
        if re.search(r'\beval\s*\(', content, re.IGNORECASE):
            threats.append("使用了eval()函数")
        
        if re.search(r'\bFunction\s*\(', content, re.IGNORECASE):
            threats.append("使用了Function()构造函数")
        
        # 检查DOM操作
        if re.search(r'\.innerHTML\s*=', content, re.IGNORECASE):
            warnings.append("使用了innerHTML赋值")
        
        # 检查网络请求
        if re.search(r'\b(?:fetch|XMLHttpRequest|axios)\b', content, re.IGNORECASE):
            warnings.append("包含网络请求代码")
    
    def _scan_css_content(self, content: str, threats: List[str], warnings: List[str]):
        """扫描CSS内容"""
        # 检查外部导入
        if re.search(r'@import\s+url\s*\(', content, re.IGNORECASE):
            warnings.append("包含外部CSS导入")
        
        # 检查IE特有的expression
        if re.search(r'expression\s*\(', content, re.IGNORECASE):
            threats.append("使用了CSS expression（IE特有，存在安全风险）")
    
    def _scan_binary_content(self, content: bytes, threats: List[str], warnings: List[str]):
        """扫描二进制内容"""
        # 检查可执行文件头
        executable_signatures = [
            b'MZ',      # Windows PE
            b'\x7fELF', # Linux ELF
            b'\xfe\xed\xfa', # macOS Mach-O
        ]
        
        for sig in executable_signatures:
            if content.startswith(sig):
                threats.append("检测到可执行文件签名")
                break
        
        # 检查压缩文件
        if content.startswith(b'PK'):  # ZIP文件
            warnings.append("包含ZIP压缩文件")
        elif content.startswith(b'\x1f\x8b'):  # GZIP文件
            warnings.append("包含GZIP压缩文件")


# 全局文件服务实例
product_file_service = ProductFileService()