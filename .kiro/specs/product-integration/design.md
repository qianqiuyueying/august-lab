# 产品嵌入功能设计文档

## 概述

产品嵌入功能将个人网站从静态作品展示平台升级为动态产品体验平台。通过在现有架构基础上增加产品容器系统，访客可以直接在个人网站内体验完整的Web应用产品，无需跳转到外部网站。

这种设计实现了"一站式个人品牌生态系统"，将作品展示、博客分享和产品体验统一在同一个网站内，大大提升了用户体验和品牌一致性。

## 架构

### 扩展后的整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        个人网站生态系统                          │
├─────────────────┬─────────────────┬─────────────────┬─────────────┤
│   前台展示网站    │   产品体验区域    │   后台管理系统    │  FastAPI后端 │
│   (Vue3 SPA)    │  (Product Zone) │   (Vue3 SPA)    │             │
│                 │                 │                 │             │
│ - 首页          │ - 产品容器       │ - 登录认证       │ - RESTful   │
│ - 作品展示      │ - 产品路由       │ - 作品管理       │   API       │
│ - 博客文章      │ - 沙箱隔离       │ - 博客管理       │ - 产品管理  │
│ - 关于我        │ - 状态管理       │ - 产品管理       │   API       │
│ - 产品入口      │ - 导航控制       │ - 统计分析       │ - 文件处理  │
└─────────────────┴─────────────────┴─────────────────┴─────────────┘
                           │                                │
                  ┌─────────────────┐                ┌─────────────────┐
                  │   产品文件存储    │                │   SQLite数据库   │
                  │                 │                │                 │
                  │ - 产品ZIP包      │                │ - 原有表结构     │
                  │ - 解压文件       │                │ - 产品元数据表   │
                  │ - 静态资源       │                │ - 产品统计表     │
                  │ - 配置文件       │                │ - 产品日志表     │
                  └─────────────────┘                └─────────────────┘
```

### 产品嵌入架构详解

**产品容器系统:**
```
┌─────────────────────────────────────────────────────────────────┐
│                        产品容器 (ProductContainer)               │
├─────────────────────────────────────────────────────────────────┤
│  导航栏: [返回主站] [全屏切换] [产品信息] [设置]                    │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                    产品应用区域                              │ │
│  │  ┌─────────────────────────────────────────────────────────┐ │ │
│  │  │                 iframe 沙箱                            │ │ │
│  │  │  ┌─────────────────────────────────────────────────────┐ │ │ │
│  │  │  │              嵌入的产品应用                          │ │ │ │
│  │  │  │  - HTML/CSS/JavaScript                            │ │ │ │
│  │  │  │  - React/Vue/Angular SPA                         │ │ │ │
│  │  │  │  - Canvas/WebGL 游戏                             │ │ │ │
│  │  │  │  - 在线工具应用                                    │ │ │ │
│  │  │  └─────────────────────────────────────────────────────┘ │ │ │
│  │  └─────────────────────────────────────────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│  状态栏: [加载状态] [错误信息] [使用统计] [帮助]                    │
└─────────────────────────────────────────────────────────────────┘
```

## 组件和接口

### 新增前端组件

**产品相关组件:**
```
src/frontend/
├── components/
│   └── product/
│       ├── ProductContainer.vue    # 产品容器主组件
│       ├── ProductNavbar.vue       # 产品导航栏
│       ├── ProductIframe.vue       # 产品iframe容器
│       ├── ProductLoader.vue       # 产品加载组件
│       ├── ProductError.vue        # 产品错误处理
│       └── ProductControls.vue     # 产品控制面板
├── pages/
│   └── ProductPage.vue             # 产品页面
└── router/
    └── productRoutes.ts            # 产品路由配置
```

**后台管理组件:**
```
src/admin/
├── components/
│   └── product/
│       ├── ProductTable.vue        # 产品管理表格
│       ├── ProductForm.vue         # 产品编辑表单
│       ├── ProductUpload.vue       # 产品文件上传
│       ├── ProductPreview.vue      # 产品预览
│       └── ProductStats.vue        # 产品统计
└── pages/
    ├── ProductManagement.vue       # 产品管理页面
    └── ProductAnalytics.vue        # 产品分析页面
```

### 新增API接口

**产品管理接口:**
```
GET    /api/products              # 获取产品列表
GET    /api/products/{id}         # 获取单个产品信息
POST   /api/products              # 创建新产品
PUT    /api/products/{id}         # 更新产品信息
DELETE /api/products/{id}         # 删除产品
POST   /api/products/{id}/upload  # 上传产品文件
GET    /api/products/{id}/files   # 获取产品文件列表
```

**产品访问接口:**
```
GET    /api/products/{id}/launch  # 启动产品应用
POST   /api/products/{id}/stats   # 记录使用统计
GET    /api/products/{id}/config  # 获取产品配置
```

**产品文件服务:**
```
GET    /products/{id}/             # 产品静态文件服务
GET    /products/{id}/index.html  # 产品入口文件
GET    /products/{id}/assets/*    # 产品资源文件
```

## 数据模型

### 新增数据库表

**产品表 (products):**
```sql
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    tech_stack TEXT,  -- JSON格式存储技术栈
    product_type VARCHAR(50) NOT NULL,  -- 'static', 'spa', 'game', 'tool'
    entry_file VARCHAR(200) DEFAULT 'index.html',
    file_path VARCHAR(500),  -- 产品文件存储路径
    config_data TEXT,  -- JSON格式存储产品配置
    is_published BOOLEAN DEFAULT FALSE,
    is_featured BOOLEAN DEFAULT FALSE,
    display_order INTEGER DEFAULT 0,
    version VARCHAR(50) DEFAULT '1.0.0',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**产品统计表 (product_stats):**
```sql
CREATE TABLE product_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    visitor_ip VARCHAR(45),
    session_id VARCHAR(100),
    access_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    duration_seconds INTEGER DEFAULT 0,
    user_agent TEXT,
    referrer VARCHAR(500),
    FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE
);
```

**产品日志表 (product_logs):**
```sql
CREATE TABLE product_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    log_type VARCHAR(50) NOT NULL,  -- 'access', 'error', 'performance'
    log_level VARCHAR(20) DEFAULT 'info',  -- 'debug', 'info', 'warning', 'error'
    message TEXT NOT NULL,
    details TEXT,  -- JSON格式存储详细信息
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE
);
```

### Pydantic数据模型

**产品相关模型:**
```python
class ProductBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    tech_stack: List[str] = Field(default_factory=list, max_items=20)
    product_type: str = Field(..., regex="^(static|spa|game|tool)$")
    entry_file: str = Field("index.html", max_length=200)
    config_data: Optional[Dict[str, Any]] = Field(default_factory=dict)
    is_published: bool = Field(False)
    is_featured: bool = Field(False)
    display_order: int = Field(0, ge=0, le=9999)
    version: str = Field("1.0.0", max_length=50)

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    tech_stack: Optional[List[str]] = None
    product_type: Optional[str] = None
    entry_file: Optional[str] = None
    config_data: Optional[Dict[str, Any]] = None
    is_published: Optional[bool] = None
    is_featured: Optional[bool] = None
    display_order: Optional[int] = None
    version: Optional[str] = None

class Product(ProductBase):
    id: int
    file_path: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ProductStats(BaseModel):
    product_id: int
    total_visits: int
    unique_visitors: int
    average_duration: float
    last_access: Optional[datetime]
    popular_times: List[Dict[str, Any]]

class ProductUploadResponse(BaseModel):
    message: str
    product_id: int
    file_path: str
    extracted_files: List[str]
```

## 正确性属性

*属性是一个特征或行为，应该在系统的所有有效执行中保持为真——本质上，是关于系统应该做什么的正式声明。属性作为人类可读规范和机器可验证正确性保证之间的桥梁。*

**属性 1: 产品文件上传完整性**
*对于任意* 有效的产品ZIP文件，上传后解压应该保持所有文件的完整性和目录结构
**验证: 需求 3.2**

**属性 2: 产品容器隔离性**
*对于任意* 嵌入的产品应用，运行时不应该能够访问主网站的DOM或全局变量
**验证: 需求 4.1, 4.2**

**属性 3: 产品路由唯一性**
*对于任意* 产品应用，每个产品应该有唯一的URL路径且不与主网站路由冲突
**验证: 需求 1.3**

**属性 4: 产品状态持久性**
*对于任意* 产品应用会话，用户离开后再次访问应该能够恢复之前的状态
**验证: 需求 6.4**

**属性 5: 产品类型支持完整性**
*对于任意* 支持的产品类型（static、spa、game、tool），系统应该能够正确加载和运行
**验证: 需求 5.1, 5.2, 5.3, 5.4**

**属性 6: 产品访问统计准确性**
*对于任意* 产品访问行为，统计数据应该准确记录访问次数、时长和用户信息
**验证: 需求 7.1, 7.2**

**属性 7: 产品错误隔离性**
*对于任意* 产品应用错误，不应该影响主网站或其他产品的正常运行
**验证: 需求 4.3**

**属性 8: 产品文件安全性**
*对于任意* 产品文件访问，只能访问该产品自己的文件和资源
**验证: 需求 4.2**

**属性 9: 产品配置有效性**
*对于任意* 产品配置参数，应该能够正确应用到产品的运行环境中
**验证: 需求 5.5**

**属性 10: 产品发布状态一致性**
*对于任意* 产品发布状态变更，前台显示应该立即反映最新的可见性设置
**验证: 需求 3.4**

**属性 11: 产品导航功能性**
*对于任意* 运行中的产品，导航栏应该始终提供返回主网站的功能
**验证: 需求 6.3**

**属性 12: 产品响应式适配性**
*对于任意* 设备屏幕尺寸，产品容器应该提供适合的显示模式
**验证: 需求 6.5**

**属性 13: 产品数据存储隔离性**
*对于任意* 产品应用，其数据存储应该与其他产品和主网站完全隔离
**验证: 需求 8.2**

**属性 14: 产品API通信安全性**
*对于任意* 产品与后端的通信，应该通过安全的认证和授权机制
**验证: 需求 8.1**

**属性 15: 产品文件完整性验证**
*对于任意* 产品文件，加载前应该验证文件的完整性和安全性
**验证: 需求 4.4**

## 错误处理

### 产品加载错误处理

**文件缺失错误:**
```javascript
// 产品入口文件不存在
{
  error_type: 'FILE_NOT_FOUND',
  message: '产品入口文件不存在',
  fallback: '显示产品信息页面'
}

// 产品资源加载失败
{
  error_type: 'RESOURCE_LOAD_ERROR',
  message: '产品资源加载失败',
  fallback: '显示重试按钮'
}
```

**产品运行错误:**
```javascript
// 产品JavaScript错误
{
  error_type: 'PRODUCT_RUNTIME_ERROR',
  message: '产品运行时错误',
  fallback: '显示错误信息和重启选项'
}

// 产品兼容性错误
{
  error_type: 'COMPATIBILITY_ERROR',
  message: '浏览器不支持该产品',
  fallback: '显示兼容性提示'
}
```

### 产品管理错误处理

**文件上传错误:**
```python
class ProductUploadError(Exception):
    def __init__(self, error_type: str, message: str, details: dict = None):
        self.error_type = error_type
        self.message = message
        self.details = details or {}

# 文件格式错误
raise ProductUploadError(
    error_type="INVALID_FILE_FORMAT",
    message="只支持ZIP格式的产品文件",
    details={"allowed_formats": [".zip"]}
)

# 文件大小超限
raise ProductUploadError(
    error_type="FILE_SIZE_EXCEEDED",
    message="产品文件大小超过限制",
    details={"max_size": "100MB", "current_size": "150MB"}
)
```

## 测试策略

### 产品嵌入功能测试

**单元测试:**
- 产品文件上传和解压功能
- 产品容器组件渲染和交互
- 产品路由配置和导航
- 产品统计数据收集和计算

**集成测试:**
- 产品完整的上传到展示流程
- 产品与主网站的集成和隔离
- 产品多类型支持和兼容性
- 产品错误处理和恢复机制

**基于属性的测试:**

```python
from hypothesis import given, strategies as st
import zipfile
import tempfile

@given(st.lists(st.text(min_size=1), min_size=1, max_size=10))
def test_product_file_upload_integrity(file_names):
    """
    Feature: product-integration, Property 1: 产品文件上传完整性
    验证ZIP文件上传后的完整性
    """
    # 创建测试ZIP文件
    with tempfile.NamedTemporaryFile(suffix='.zip') as zip_file:
        with zipfile.ZipFile(zip_file.name, 'w') as zf:
            for name in file_names:
                zf.writestr(f"{name}.txt", f"content of {name}")
        
        # 测试上传和解压
        # 验证所有文件都正确解压
        pass

@given(st.sampled_from(['static', 'spa', 'game', 'tool']))
def test_product_type_support(product_type):
    """
    Feature: product-integration, Property 5: 产品类型支持完整性
    验证不同产品类型的支持
    """
    # 测试不同类型产品的加载和运行
    pass
```

```javascript
import fc from 'fast-check';

test('Property 3: 产品路由唯一性', () => {
  fc.assert(fc.property(
    fc.array(fc.string({ minLength: 1, maxLength: 20 }), { minLength: 1, maxLength: 10 }),
    (productIds) => {
      // Feature: product-integration, Property 3: 产品路由唯一性
      // 验证产品路由的唯一性
      const routes = productIds.map(id => `/product/${id}`);
      const uniqueRoutes = [...new Set(routes)];
      return routes.length === uniqueRoutes.length;
    }
  ), { numRuns: 100 });
});
```

### 性能测试

**产品加载性能:**
- 测试不同大小产品文件的加载时间
- 验证产品容器的内存使用情况
- 测试多个产品同时运行的性能影响

**并发访问测试:**
- 测试多用户同时访问同一产品
- 验证产品统计数据的准确性
- 测试产品文件服务的并发处理能力

这个设计完全可行！主要优势包括：

1. **统一生态系统** - 所有产品都在同一个域名下，提升品牌一致性
2. **无缝用户体验** - 访客无需跳转就能体验完整产品
3. **简化维护** - 只需维护一个网站，所有产品统一管理
4. **灵活扩展** - 支持多种产品类型，未来可以轻松添加新功能
5. **安全隔离** - 通过iframe和沙箱技术确保产品间的隔离

你觉得这个设计方案如何？需要我继续创建实现计划吗？