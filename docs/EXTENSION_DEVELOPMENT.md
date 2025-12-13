# 产品扩展开发指南

## 概述

产品扩展机制允许开发者创建自定义的产品类型、渲染器、验证器、处理器、钩子和中间件，以扩展系统的功能。

## 扩展类型

### 1. 产品类型扩展 (ProductTypeExtension)

用于支持新的产品类型，如游戏、工具、应用等。

```python
from backend.app.services.product_extension_service import (
    ProductTypeExtension, ExtensionMetadata, ProductTypeDefinition, ExtensionType
)

class MyProductTypeExtension(ProductTypeExtension):
    def get_metadata(self) -> ExtensionMetadata:
        return ExtensionMetadata(
            name="my_extension",
            version="1.0.0",
            description="我的产品类型扩展",
            author="开发者",
            extension_type=ExtensionType.PRODUCT_TYPE,
            dependencies=[],
            config_schema={}
        )
    
    def get_product_type_definition(self) -> ProductTypeDefinition:
        return ProductTypeDefinition(
            type_name="my_type",
            display_name="我的产品类型",
            description="支持特定类型的产品",
            file_extensions=[".html", ".js", ".css"],
            entry_files=["index.html"],
            config_schema={},
            renderer_class="my_renderer"
        )
    
    def validate_product_files(self, files: Dict[str, bytes]) -> tuple[bool, str]:
        # 验证产品文件
        return True, ""
    
    def process_product_files(self, files: Dict[str, bytes]) -> Dict[str, bytes]:
        # 处理产品文件（可选）
        return files
```

### 2. 渲染器扩展 (ProductRenderer)

用于自定义产品的渲染方式。

```python
from backend.app.services.product_extension_service import ProductRenderer

class MyRenderer(ProductRenderer):
    def get_metadata(self) -> ExtensionMetadata:
        return ExtensionMetadata(
            name="my_renderer",
            version="1.0.0",
            description="我的渲染器",
            author="开发者",
            extension_type=ExtensionType.RENDERER,
            dependencies=["my_extension"],
            config_schema={}
        )
    
    def render_product(self, product_id: int, config: Dict[str, any]) -> str:
        # 返回渲染的HTML
        return f"<div>产品 {product_id} 的自定义渲染</div>"
    
    def get_required_assets(self) -> List[str]:
        # 返回所需的CSS/JS资源
        return []
```

### 3. 钩子扩展 (ProductHook)

用于在特定事件发生时执行自定义逻辑。

```python
from backend.app.services.product_extension_service import ProductHook, HookType

class MyHook(ProductHook):
    def get_metadata(self) -> ExtensionMetadata:
        return ExtensionMetadata(
            name="my_hook",
            version="1.0.0",
            description="我的钩子",
            author="开发者",
            extension_type=ExtensionType.HOOK,
            dependencies=[],
            config_schema={}
        )
    
    def get_hook_type(self) -> HookType:
        return HookType.AFTER_UPLOAD
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # 执行钩子逻辑
        print(f"钩子执行: {context}")
        return context
```

## 扩展目录结构

每个扩展应该放在 `extensions/` 目录下的独立文件夹中：

```
extensions/
├── my_extension/
│   ├── extension.json      # 扩展配置文件
│   ├── main.py            # 扩展主文件
│   ├── assets/            # 资源文件（可选）
│   └── templates/         # 模板文件（可选）
```

### extension.json 配置文件

```json
{
  "name": "my_extension",
  "version": "1.0.0",
  "description": "我的扩展描述",
  "author": "开发者名称",
  "homepage": "https://example.com",
  "repository": "https://github.com/example/my-extension",
  "license": "MIT",
  "keywords": ["keyword1", "keyword2"],
  "requirements": {
    "python": ">=3.8",
    "system_version": ">=1.0.0"
  },
  "config": {
    "option1": "value1",
    "option2": true
  },
  "permissions": [
    "file_access",
    "network_access"
  ],
  "assets": [
    "assets/style.css",
    "assets/script.js"
  ]
}
```

## 钩子类型

系统支持以下钩子类型：

- `BEFORE_UPLOAD`: 产品上传前
- `AFTER_UPLOAD`: 产品上传后
- `BEFORE_LAUNCH`: 产品启动前
- `AFTER_LAUNCH`: 产品启动后
- `BEFORE_DELETE`: 产品删除前
- `AFTER_DELETE`: 产品删除后
- `ON_ERROR`: 发生错误时
- `ON_ACCESS`: 产品访问时

## 开发最佳实践

### 1. 错误处理

```python
def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
    try:
        # 扩展逻辑
        return context
    except Exception as e:
        logger.error(f"扩展执行失败: {str(e)}")
        return context  # 返回原始上下文，不影响系统运行
```

### 2. 配置验证

```python
def validate_config(self, config: Dict[str, Any]) -> bool:
    required_keys = ['option1', 'option2']
    return all(key in config for key in required_keys)
```

### 3. 资源清理

```python
def cleanup(self) -> bool:
    try:
        # 清理资源
        return True
    except Exception as e:
        logger.error(f"清理失败: {str(e)}")
        return False
```

## 扩展安装

### 1. 手动安装

将扩展文件夹复制到 `extensions/` 目录，然后调用重新加载API：

```bash
POST /api/products/extensions/reload
```

### 2. API安装

```bash
POST /api/products/extensions/install
{
  "path": "/path/to/extension",
  "config": {}
}
```

## 扩展管理

### 1. 列出扩展

```bash
GET /api/products/extensions
```

### 2. 获取扩展信息

```bash
GET /api/products/extensions/{extension_name}
```

### 3. 配置扩展

```bash
POST /api/products/extensions/{extension_name}/configure
{
  "option1": "new_value",
  "option2": false
}
```

### 4. 卸载扩展

```bash
DELETE /api/products/extensions/{extension_name}
```

## 示例扩展

系统包含以下示例扩展：

1. **game_extension**: 游戏产品类型支持
2. **tool_extension**: 工具产品类型支持
3. **analytics_hook**: 访问分析钩子

可以参考这些示例来开发自己的扩展。

## 调试和测试

### 1. 日志记录

```python
import logging
logger = logging.getLogger(__name__)

logger.info("扩展信息")
logger.error("扩展错误")
```

### 2. 测试扩展

```python
# 测试扩展加载
extension = MyExtension()
metadata = extension.get_metadata()
assert metadata.name == "my_extension"

# 测试功能
result = extension.validate_product_files(test_files)
assert result[0] == True
```

## 常见问题

### Q: 扩展加载失败怎么办？

A: 检查以下几点：
1. `main.py` 文件是否存在
2. 扩展类是否正确继承基类
3. 依赖是否满足
4. 配置是否有效

### Q: 如何调试扩展？

A: 可以通过日志查看扩展的执行情况，或者在开发环境中直接调试Python代码。

### Q: 扩展之间如何通信？

A: 可以通过上下文对象传递数据，或者使用依赖关系来确保执行顺序。

## 贡献指南

欢迎贡献新的扩展！请遵循以下步骤：

1. Fork 项目
2. 创建扩展分支
3. 开发和测试扩展
4. 提交 Pull Request
5. 等待代码审查

更多信息请参考项目的贡献指南。