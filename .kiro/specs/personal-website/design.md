# 个人网站设计文档

## 概述

个人网站是一个现代化的全栈Web应用程序，采用前后端分离架构。前端使用Vue3 + Element Plus构建，包含面向访客的展示网站和管理员专用的后台管理系统。后端使用FastAPI框架提供RESTful API服务，SQLite作为数据存储解决方案。

系统设计重点关注用户体验、内容管理效率和系统可维护性，确保前台展示具有独特的视觉风格，后台管理操作简洁高效。

## 架构

### 整体架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   前台展示网站    │    │   后台管理系统    │    │   FastAPI后端    │
│   (Vue3 SPA)    │    │   (Vue3 SPA)    │    │                │
│                 │    │                 │    │                 │
│ - 首页          │    │ - 登录认证       │    │ - RESTful API   │
│ - 作品展示      │◄───┤ - 作品管理       │◄───┤ - 数据验证      │
│ - 博客文章      │    │ - 博客管理       │    │ - 文件处理      │
│ - 关于我        │    │ - 个人信息管理    │    │ - 会话管理      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                                               ┌─────────────────┐
                                               │   SQLite数据库   │
                                               │                 │
                                               │ - 作品表        │
                                               │ - 博客表        │
                                               │ - 个人信息表     │
                                               │ - 会话表        │
                                               └─────────────────┘
```

### 技术栈

**前端技术栈:**
- Vue 3 (Composition API)
- Vue Router 4 (路由管理)
- Element Plus (后台UI组件库)
- Axios (HTTP客户端)
- Vite (构建工具)
- TypeScript (类型安全)
- Tailwind CSS (前台自定义样式)

**后端技术栈:**
- FastAPI (Web框架)
- SQLAlchemy (ORM)
- Pydantic (数据验证)
- SQLite (数据库)
- Python-multipart (文件上传)
- Passlib (密码处理)
- Python-jose (JWT令牌)

## 组件和接口

### 前端组件架构

**前台展示系统组件:**
```
src/frontend/
├── components/
│   ├── common/
│   │   ├── Header.vue          # 导航头部
│   │   ├── Footer.vue          # 页脚
│   │   └── Loading.vue         # 加载组件
│   ├── home/
│   │   ├── HeroSection.vue     # 首页主视觉
│   │   ├── LatestWorks.vue     # 最新作品预览
│   │   └── LatestBlogs.vue     # 最新博客预览
│   ├── portfolio/
│   │   ├── PortfolioGrid.vue   # 作品网格
│   │   ├── PortfolioCard.vue   # 作品卡片
│   │   └── PortfolioDetail.vue # 作品详情
│   ├── blog/
│   │   ├── BlogList.vue        # 博客列表
│   │   ├── BlogCard.vue        # 博客卡片
│   │   └── BlogDetail.vue      # 博客详情
│   └── about/
│       ├── PersonalInfo.vue    # 个人信息
│       ├── SkillsSection.vue   # 技能展示
│       └── ContactInfo.vue     # 联系信息
```

**后台管理系统组件:**
```
src/admin/
├── components/
│   ├── layout/
│   │   ├── AdminLayout.vue     # 管理后台布局
│   │   ├── Sidebar.vue         # 侧边栏
│   │   └── TopBar.vue          # 顶部栏
│   ├── auth/
│   │   └── LoginForm.vue       # 登录表单
│   ├── portfolio/
│   │   ├── PortfolioTable.vue  # 作品管理表格
│   │   └── PortfolioForm.vue   # 作品编辑表单
│   ├── blog/
│   │   ├── BlogTable.vue       # 博客管理表格
│   │   ├── BlogForm.vue        # 博客编辑表单
│   │   └── MarkdownEditor.vue  # Markdown编辑器
│   └── profile/
│       └── ProfileForm.vue     # 个人信息表单
```

### API接口设计

**认证接口:**
```
POST /api/auth/login          # 管理员登录
POST /api/auth/logout         # 管理员登出
GET  /api/auth/verify         # 验证登录状态
```

**作品管理接口:**
```
GET    /api/portfolio         # 获取作品列表
GET    /api/portfolio/{id}    # 获取单个作品
POST   /api/portfolio         # 创建作品
PUT    /api/portfolio/{id}    # 更新作品
DELETE /api/portfolio/{id}    # 删除作品
```

**博客管理接口:**
```
GET    /api/blog              # 获取博客列表
GET    /api/blog/{id}         # 获取单篇博客
POST   /api/blog              # 创建博客
PUT    /api/blog/{id}         # 更新博客
DELETE /api/blog/{id}         # 删除博客
```

**个人信息接口:**
```
GET    /api/profile           # 获取个人信息
PUT    /api/profile           # 更新个人信息
```

**文件上传接口:**
```
POST   /api/upload/image      # 上传图片文件
```

## 数据模型

### 数据库表结构

**作品表 (portfolio):**
```sql
CREATE TABLE portfolio (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    tech_stack TEXT,  -- JSON格式存储技术栈数组
    project_url VARCHAR(500),
    github_url VARCHAR(500),
    image_url VARCHAR(500),
    display_order INTEGER DEFAULT 0,
    is_featured BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**博客表 (blog):**
```sql
CREATE TABLE blog (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    summary TEXT,
    tags TEXT,  -- JSON格式存储标签数组
    is_published BOOLEAN DEFAULT FALSE,
    cover_image VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    published_at TIMESTAMP
);
```

**个人信息表 (profile):**
```sql
CREATE TABLE profile (
    id INTEGER PRIMARY KEY DEFAULT 1,
    name VARCHAR(100) NOT NULL,
    title VARCHAR(200),
    bio TEXT,
    avatar_url VARCHAR(500),
    email VARCHAR(100),
    github_url VARCHAR(500),
    linkedin_url VARCHAR(500),
    twitter_url VARCHAR(500),
    skills TEXT,  -- JSON格式存储技能数组
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**会话表 (sessions):**
```sql
CREATE TABLE sessions (
    id VARCHAR(100) PRIMARY KEY,
    user_id VARCHAR(50) DEFAULT 'admin',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);
```

### Pydantic数据模型

**作品相关模型:**
```python
class PortfolioBase(BaseModel):
    title: str
    description: Optional[str] = None
    tech_stack: List[str] = []
    project_url: Optional[str] = None
    github_url: Optional[str] = None
    image_url: Optional[str] = None
    display_order: int = 0
    is_featured: bool = False

class PortfolioCreate(PortfolioBase):
    pass

class PortfolioUpdate(PortfolioBase):
    title: Optional[str] = None

class Portfolio(PortfolioBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
```

**博客相关模型:**
```python
class BlogBase(BaseModel):
    title: str
    content: str
    summary: Optional[str] = None
    tags: List[str] = []
    is_published: bool = False
    cover_image: Optional[str] = None

class BlogCreate(BlogBase):
    pass

class BlogUpdate(BlogBase):
    title: Optional[str] = None
    content: Optional[str] = None

class Blog(BlogBase):
    id: int
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
```

## 正确性属性

*属性是一个特征或行为，应该在系统的所有有效执行中保持为真——本质上，是关于系统应该做什么的正式声明。属性作为人类可读规范和机器可验证正确性保证之间的桥梁。*
**属性 1: 导航功能完整性**
*对于任意* 前台页面，所有导航链接都应该能够正确跳转到对应的目标页面
**验证: 需求 1.2**

**属性 2: 响应式布局适配**
*对于任意* 屏幕尺寸，前台页面都应该提供适合该尺寸的布局和交互体验
**验证: 需求 1.4**

**属性 3: 内容列表显示完整性**
*对于任意* 内容类型（作品或博客），前台页面应该显示所有已发布的内容项目
**验证: 需求 2.1, 3.1**

**属性 4: 内容详情信息完整性**
*对于任意* 内容项目，详情页面应该包含该项目的所有必需信息字段
**验证: 需求 2.2, 3.2**

**属性 5: 内容排序一致性**
*对于任意* 内容列表，显示顺序应该与指定的排序规则保持一致
**验证: 需求 2.3, 3.3**

**属性 6: Markdown解析往返一致性**
*对于任意* 有效的Markdown文本，解析后渲染的内容应该保持原始语义和格式
**验证: 需求 3.4**

**属性 7: 图片资源加载可靠性**
*对于任意* 包含图片的内容项目，图片资源都应该能够正确加载和显示
**验证: 需求 2.5, 4.2**

**属性 8: 联系链接功能性**
*对于任意* 联系方式链接，点击后应该能够正确跳转到对应的联系平台
**验证: 需求 4.3**

**属性 9: 数据同步实时性**
*对于任意* 后台数据更新操作，前台显示内容应该立即反映最新的数据状态
**验证: 需求 4.5, 8.5**

**属性 10: 认证凭据验证准确性**
*对于任意* 登录凭据输入，系统应该准确验证并返回相应的认证结果
**验证: 需求 5.2, 5.3**

**属性 11: 会话管理生命周期**
*对于任意* 用户会话，系统应该正确管理会话的创建、维护和销毁过程
**验证: 需求 5.4, 5.5**

**属性 12: CRUD操作数据完整性**
*对于任意* 内容管理操作（创建、读取、更新、删除），操作结果应该正确反映在数据存储中
**验证: 需求 6.2, 6.3, 6.4, 7.2, 7.3, 7.4**

**属性 13: 数据持久化往返一致性**
*对于任意* 数据对象，保存到数据库后再读取应该得到等价的数据内容
**验证: 需求 6.5, 7.5**

**属性 14: 文件上传处理完整性**
*对于任意* 有效的图片文件，上传处理后应该能够正确存储并提供访问路径
**验证: 需求 8.3, 10.5**

**属性 15: 数据验证规则一致性**
*对于任意* 输入数据，验证规则应该在前端和后端保持一致的执行结果
**验证: 需求 8.4, 10.3**

**属性 16: 数据库事务原子性**
*对于任意* 数据库操作序列，事务应该确保要么全部成功要么全部回滚
**验证: 需求 9.2**

**属性 17: 数据库备份往返一致性**
*对于任意* 数据库状态，备份后恢复应该得到完全相同的数据内容
**验证: 需求 9.4**

**属性 18: SQL注入防护有效性**
*对于任意* 包含恶意SQL代码的输入，参数化查询应该防止代码执行
**验证: 需求 9.5**

**属性 19: API响应格式规范性**
*对于任意* API请求，响应应该使用标准JSON格式并包含正确的HTTP状态码
**验证: 需求 10.1, 10.2**

**属性 20: API错误处理一致性**
*对于任意* API错误情况，响应应该包含结构化的错误信息和适当的错误代码
**验证: 需求 10.4**

## 错误处理

### 前端错误处理策略

**网络错误处理:**
- 实现全局HTTP拦截器处理网络请求错误
- 提供用户友好的错误提示信息
- 支持请求重试机制
- 实现离线状态检测和提示

**数据加载错误:**
- 图片加载失败时显示占位符
- 内容加载失败时显示重试按钮
- 实现骨架屏提升加载体验

**表单验证错误:**
- 实时表单验证和错误提示
- 统一的错误信息显示样式
- 防止重复提交机制

### 后端错误处理策略

**数据库错误处理:**
- 数据库连接失败时的重连机制
- 事务回滚和错误恢复
- 数据完整性约束违反的处理

**文件处理错误:**
- 文件上传大小和格式限制
- 文件存储空间不足的处理
- 文件访问权限错误的处理

**API错误响应:**
```python
class APIError(BaseModel):
    error_code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)

# 标准错误响应格式
{
    "error": {
        "error_code": "VALIDATION_ERROR",
        "message": "输入数据验证失败",
        "details": {
            "field": "title",
            "reason": "标题不能为空"
        },
        "timestamp": "2024-01-01T12:00:00Z"
    }
}
```

## 测试策略

### 双重测试方法

本项目采用单元测试和基于属性的测试相结合的综合测试策略：

**单元测试:**
- 验证特定示例、边界情况和错误条件
- 测试组件集成点
- 覆盖具体的业务逻辑场景

**基于属性的测试:**
- 验证应该在所有输入中保持的通用属性
- 使用随机生成的测试数据验证系统行为
- 每个属性测试运行最少100次迭代

### 前端测试策略

**单元测试框架:** Vitest + Vue Test Utils
**组件测试:**
- 测试组件渲染和用户交互
- 验证props传递和事件触发
- 测试条件渲染和状态变化

**集成测试:**
- 测试路由导航功能
- 验证API调用和数据流
- 测试用户完整操作流程

### 后端测试策略

**单元测试框架:** pytest + pytest-asyncio
**API测试:**
- 测试所有API端点的CRUD操作
- 验证请求参数验证和响应格式
- 测试认证和权限控制

**数据库测试:**
- 使用内存SQLite进行测试隔离
- 测试数据模型和关系约束
- 验证事务处理和数据一致性

### 基于属性的测试配置

**Python端使用Hypothesis库:**
```python
from hypothesis import given, strategies as st

@given(st.text(min_size=1, max_size=200))
def test_portfolio_title_property(title):
    """
    Feature: personal-website, Property 12: CRUD操作数据完整性
    验证作品标题的创建和读取操作
    """
    # 测试逻辑
```

**JavaScript端使用fast-check库:**
```javascript
import fc from 'fast-check';

test('Property 1: 导航功能完整性', () => {
  fc.assert(fc.property(
    fc.constantFrom('home', 'portfolio', 'blog', 'about'),
    (page) => {
      // Feature: personal-website, Property 1: 导航功能完整性
      // 测试逻辑
    }
  ), { numRuns: 100 });
});
```

**测试要求:**
- 每个基于属性的测试必须运行最少100次迭代
- 每个测试必须使用注释明确标识对应的设计文档属性
- 测试标签格式: `Feature: personal-website, Property {number}: {property_text}`
- 每个正确性属性必须由单一的基于属性的测试实现

### 测试数据生成策略

**智能生成器设计:**
- 为作品数据生成合理的标题、描述和技术栈组合
- 为博客内容生成有效的Markdown格式文本
- 为个人信息生成符合格式要求的联系方式
- 为文件上传生成不同格式和大小的测试图片

**边界条件覆盖:**
- 空数据和最大长度数据的处理
- 特殊字符和Unicode字符的处理
- 无效文件格式和超大文件的处理
- 网络异常和数据库连接失败的模拟