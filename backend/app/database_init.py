"""
数据库初始化脚本
用于创建数据库表和初始化数据
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from .database import Base, SQLALCHEMY_DATABASE_URL
from .models import Portfolio, Blog, Profile, Session, Product, ProductStats, ProductLog, ProductFeedback
import json
from datetime import datetime, timezone

def init_database():
    """初始化数据库"""
    print("正在初始化数据库...")
    
    # 创建引擎
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    print("数据库表创建完成")
    
    # 创建会话
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # 初始化示例数据
        init_sample_data(db)
        print("示例数据初始化完成")
    except Exception as e:
        print(f"初始化示例数据时出错: {e}")
        db.rollback()
    finally:
        db.close()
    
    print("数据库初始化完成！")

def init_sample_data(db):
    """初始化示例数据"""
    
    # 检查是否已有数据
    if db.query(Portfolio).first() or db.query(Blog).first() or db.query(Profile).first() or db.query(Product).first():
        print("数据库已包含数据，跳过示例数据初始化")
        return
    
    # 创建示例个人信息
    profile = Profile(
        id=1,
        name="August",
        title="全栈开发者 & 技术爱好者",
        bio="我是一名热爱技术的开发者，专注于前端和后端开发。喜欢探索新技术，分享学习心得，致力于创造有意义的数字体验。在工作之余，我也喜欢写博客、参与开源项目，与技术社区保持交流。",
        email="august@example.com",
        github_url="https://github.com/august-dev",
        linkedin_url="https://linkedin.com/in/august-dev",
        twitter_url="https://twitter.com/august_dev",
        skills=[
            {"name": "Vue.js", "level": 90, "category": "frontend"},
            {"name": "React", "level": 85, "category": "frontend"},
            {"name": "TypeScript", "level": 88, "category": "frontend"},
            {"name": "Tailwind CSS", "level": 92, "category": "frontend"},
            {"name": "Node.js", "level": 85, "category": "backend"},
            {"name": "Python", "level": 80, "category": "backend"},
            {"name": "FastAPI", "level": 75, "category": "backend"},
            {"name": "PostgreSQL", "level": 78, "category": "database"},
            {"name": "SQLite", "level": 82, "category": "database"},
            {"name": "Git", "level": 88, "category": "tools"},
            {"name": "Docker", "level": 75, "category": "tools"}
        ]
    )
    db.add(profile)
    
    # 创建示例作品
    portfolios = [
        Portfolio(
            title="个人网站项目",
            description="使用Vue3和FastAPI构建的现代化个人网站，包含前台展示和后台管理系统。采用响应式设计，支持博客文章管理、作品展示和个人信息管理。",
            tech_stack=["Vue3", "TypeScript", "FastAPI", "SQLite", "Tailwind CSS", "Element Plus"],
            project_url="https://august.lab",
            github_url="https://github.com/august-dev/personal-website",
            image_url="https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800&h=450&fit=crop",
            display_order=1,
            is_featured=True
        ),
        Portfolio(
            title="任务管理应用",
            description="一个简洁高效的任务管理应用，支持任务创建、分类、优先级设置和进度跟踪。使用现代化的UI设计，提供良好的用户体验。",
            tech_stack=["React", "Node.js", "MongoDB", "Express", "Material-UI"],
            project_url="https://taskapp.example.com",
            github_url="https://github.com/august-dev/task-manager",
            image_url="https://images.unsplash.com/photo-1611224923853-80b023f02d71?w=800&h=450&fit=crop",
            display_order=2,
            is_featured=False
        ),
        Portfolio(
            title="数据可视化仪表盘",
            description="企业级数据可视化仪表盘，支持多种图表类型和实时数据更新。提供灵活的配置选项和交互式数据探索功能。",
            tech_stack=["Vue3", "D3.js", "Python", "Django", "PostgreSQL", "Redis"],
            project_url="https://dashboard.example.com",
            github_url="https://github.com/august-dev/data-dashboard",
            image_url="https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&h=450&fit=crop",
            display_order=3,
            is_featured=True
        )
    ]
    
    for portfolio in portfolios:
        db.add(portfolio)
    
    # 创建示例博客文章
    blogs = [
        Blog(
            title="Vue3 Composition API 实践指南",
            content="""# Vue3 Composition API 实践指南

Vue3 的 Composition API 为我们提供了更灵活的组件逻辑组织方式。本文将深入探讨如何在实际项目中有效使用 Composition API。

## 什么是 Composition API

Composition API 是 Vue3 引入的新特性，它允许我们使用函数的方式来组织组件逻辑，而不是传统的选项式 API。

## 主要优势

1. **更好的逻辑复用**：通过组合函数，我们可以轻松地在不同组件间共享逻辑
2. **更好的类型推导**：TypeScript 支持更加完善
3. **更灵活的代码组织**：相关逻辑可以组织在一起

## 实践示例

```javascript
import { ref, computed, onMounted } from 'vue'

export default {
  setup() {
    const count = ref(0)
    const doubleCount = computed(() => count.value * 2)
    
    const increment = () => {
      count.value++
    }
    
    onMounted(() => {
      console.log('组件已挂载')
    })
    
    return {
      count,
      doubleCount,
      increment
    }
  }
}
```

## 总结

Composition API 为 Vue3 带来了更强大的功能和更好的开发体验。通过合理使用，我们可以写出更加清晰和可维护的代码。""",
            summary="深入探讨Vue3 Composition API的使用方法和最佳实践，包含实际代码示例和应用场景分析。",
            tags=["Vue3", "前端开发", "JavaScript", "Composition API"],
            cover_image="https://images.unsplash.com/photo-1633356122544-f134324a6cee?w=800&h=450&fit=crop",
            is_published=True,
            published_at=datetime.now(timezone.utc)
        ),
        Blog(
            title="FastAPI 快速入门教程",
            content="""# FastAPI 快速入门教程

FastAPI 是一个现代、快速的 Python Web 框架，用于构建 API。它基于标准 Python 类型提示，具有出色的性能和开发体验。

## 为什么选择 FastAPI

- **高性能**：与 NodeJS 和 Go 相当的性能
- **快速开发**：相比其他框架，开发速度提升 200-300%
- **自动文档**：自动生成交互式 API 文档
- **类型安全**：基于 Python 类型提示

## 快速开始

### 安装

```bash
pip install fastapi uvicorn
```

### 创建第一个 API

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/items/{item_id}")
async def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}
```

### 运行应用

```bash
uvicorn main:app --reload
```

## 数据验证

FastAPI 使用 Pydantic 进行数据验证：

```python
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    price: float
    is_offer: bool = False

@app.post("/items/")
async def create_item(item: Item):
    return item
```

## 总结

FastAPI 提供了现代化的 API 开发体验，结合了高性能和易用性。它是构建现代 Web API 的绝佳选择。""",
            summary="FastAPI 框架的入门教程，涵盖安装、基础用法、数据验证等核心概念，适合初学者快速上手。",
            tags=["Python", "FastAPI", "后端开发", "API"],
            cover_image="https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=800&h=450&fit=crop",
            is_published=True,
            published_at=datetime.now(timezone.utc)
        ),
        Blog(
            title="现代前端开发工具链指南",
            content="""# 现代前端开发工具链指南

现代前端开发涉及众多工具和技术。本文将介绍一个完整的前端开发工具链，帮助提升开发效率和代码质量。

## 核心工具

### 构建工具
- **Vite**：下一代前端构建工具
- **Webpack**：成熟的模块打包器
- **Rollup**：专注于库开发的打包工具

### 开发框架
- **Vue3**：渐进式 JavaScript 框架
- **React**：用于构建用户界面的库
- **Angular**：完整的应用开发平台

### 样式解决方案
- **Tailwind CSS**：实用优先的 CSS 框架
- **Sass/SCSS**：CSS 预处理器
- **CSS Modules**：局部作用域 CSS

## 开发流程

1. **项目初始化**：使用脚手架工具快速创建项目
2. **开发环境**：配置热重载和开发服务器
3. **代码规范**：ESLint + Prettier 保证代码质量
4. **测试**：单元测试和集成测试
5. **构建部署**：优化打包和自动化部署

## 最佳实践

- 使用 TypeScript 提供类型安全
- 配置 Git hooks 进行代码检查
- 实施持续集成和持续部署
- 监控应用性能和错误

## 总结

选择合适的工具链对项目成功至关重要。根据项目需求和团队经验，选择最适合的技术栈。""",
            summary="全面介绍现代前端开发工具链，包括构建工具、开发框架、样式解决方案等，提供最佳实践建议。",
            tags=["前端开发", "工具链", "Vite", "构建工具"],
            cover_image="https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=800&h=450&fit=crop",
            is_published=False  # 草稿状态
        )
    ]
    
    for blog in blogs:
        db.add(blog)
    
    # 创建示例产品
    products = [
        Product(
            title="在线计算器",
            description="一个功能完整的在线科学计算器，支持基础运算、三角函数、对数等高级计算功能。界面简洁美观，支持键盘快捷键操作。",
            tech_stack=["HTML", "CSS", "JavaScript", "Math.js"],
            product_type="tool",
            entry_file="index.html",
            config_data={
                "theme": "modern",
                "precision": 10,
                "history_enabled": True
            },
            is_published=True,
            is_featured=True,
            display_order=1,
            version="2.1.0"
        ),
        Product(
            title="贪吃蛇游戏",
            description="经典的贪吃蛇游戏，使用Canvas技术实现。包含多种难度级别、积分系统和排行榜功能。支持触屏和键盘操作。",
            tech_stack=["HTML5", "Canvas", "JavaScript", "CSS3"],
            product_type="game",
            entry_file="game.html",
            config_data={
                "max_score_records": 10,
                "default_speed": 150,
                "grid_size": 20
            },
            is_published=True,
            is_featured=False,
            display_order=2,
            version="1.5.2"
        ),
        Product(
            title="Markdown编辑器",
            description="实时预览的Markdown编辑器，支持语法高亮、文件导入导出、主题切换等功能。适合写作和文档编辑。",
            tech_stack=["Vue3", "CodeMirror", "Marked", "Highlight.js"],
            product_type="spa",
            entry_file="index.html",
            config_data={
                "auto_save": True,
                "vim_mode": False,
                "theme": "github"
            },
            is_published=False,  # 开发中
            is_featured=False,
            display_order=3,
            version="0.8.0"
        )
    ]
    
    for product in products:
        db.add(product)
    
    # 提交所有更改
    db.commit()
    print("示例数据创建完成")

def reset_database():
    """重置数据库（删除所有表并重新创建）"""
    print("正在重置数据库...")
    
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    
    # 删除所有表
    Base.metadata.drop_all(bind=engine)
    print("已删除所有表")
    
    # 重新初始化
    init_database()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--reset":
        reset_database()
    else:
        init_database()