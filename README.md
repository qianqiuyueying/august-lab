# August.Lab - 个人网站与产品展示平台

一个现代化的全栈个人网站项目，采用前后端分离架构，包含前台展示、后台管理系统和产品嵌入功能。项目基于规范驱动开发（Spec-Driven Development）方法构建，具有完整的需求分析、设计文档和实现计划。支持在个人网站内直接嵌入和展示完整的Web应用产品，形成统一的个人品牌生态系统。

## 🎯 项目状态

✅ **生产就绪** - 项目已完成核心功能开发，包含完整的部署配置、安全加固和CI/CD流程，可直接部署到生产环境。

### 最新更新
- ✅ 环境变量配置管理
- ✅ Docker 容器化支持
- ✅ CI/CD 自动化流程
- ✅ 速率限制和安全加固
- ✅ 数据库连接池优化
- ✅ 自动化备份脚本

## ✨ 功能特性

### 前台展示系统
- 🏠 **现代化首页** - 响应式设计，展示最新作品、产品和博客预览
- 💼 **作品展示** - 项目作品列表和详情页面，支持技术栈展示和项目链接
- 🚀 **产品体验** - 直接在网站内体验完整的Web应用产品，无需跳转
- 📝 **博客系统** - Markdown文章渲染，支持标签分类和阅读时间估算
- 👤 **关于我页面** - 个人信息展示，技能可视化和联系方式
- 📱 **响应式设计** - 完美适配移动端和桌面端

### 产品嵌入系统
- 🎯 **产品容器** - 安全的iframe沙箱，支持多种产品类型
- 🔧 **产品管理** - 上传、配置、发布和版本管理
- 📊 **使用统计** - 访问量、使用时长和用户行为分析
- 🛡️ **安全隔离** - 产品间完全隔离，不影响主网站运行
- 🎮 **多类型支持** - 静态网站、SPA应用、游戏、在线工具
- 💾 **数据存储** - 产品专用数据存储空间和API通信
- 👥 **用户系统** - 产品内用户认证和个性化设置
- 📝 **反馈收集** - 用户评价、建议和错误报告

### 后台管理系统
- 🔐 **安全登录** - 会话管理和路由守卫
- 📊 **仪表盘** - 实时统计数据和快速操作
- 💼 **作品管理** - CRUD操作，图片上传，Markdown编辑
- 🚀 **产品管理** - 产品上传、配置、发布和监控
- 📈 **产品分析** - 使用统计、性能监控和错误日志
- 🔧 **API管理** - 产品API令牌、权限和调用监控
- 💾 **数据管理** - 产品数据存储、备份和恢复
- 📝 **博客管理** - 文章编辑，发布状态管理，SEO设置
- 👤 **个人信息管理** - 富文本编辑，头像上传，技能管理
- 🔄 **实时数据同步** - 前后端数据一致性保证

### 技术特性
- 🚀 **高性能API** - FastAPI异步处理，自动API文档
- 🛡️ **安全防护** - SQL注入防护，数据验证，错误处理
- 🧪 **属性测试** - 基于Hypothesis的属性测试，150+个测试用例
- 📦 **模块化架构** - 清晰的代码组织和组件复用
- 🎨 **现代UI** - Tailwind CSS + Element Plus
- 🔒 **产品安全** - iframe沙箱隔离，API令牌认证
- 📊 **实时监控** - 产品性能监控，错误日志，使用统计
- 🔄 **数据同步** - 产品用户系统集成，会话管理

## 🛠️ 技术栈

### 前端技术
- **框架**: Vue 3 (Composition API) + TypeScript
- **路由**: Vue Router 4
- **UI组件**: Element Plus (管理后台) + Tailwind CSS (前台)
- **构建工具**: Vite
- **状态管理**: Composables + Pinia
- **HTTP客户端**: Axios
- **Markdown渲染**: Marked + Highlight.js
- **安全**: DOMPurify

### 后端技术
- **框架**: FastAPI + Uvicorn
- **数据库**: SQLAlchemy + SQLite
- **数据验证**: Pydantic
- **认证**: 会话管理 + 环境变量配置
- **文件处理**: Python-multipart + Pillow
- **测试**: Pytest + Hypothesis
- **安全**: SQL注入防护 + 速率限制 + CORS控制

### 开发工具
- **测试**: Vitest (前端) + Pytest (后端)
- **属性测试**: Hypothesis (Python) + Fast-check (JavaScript)
- **代码质量**: TypeScript + ESLint + Prettier
- **API文档**: FastAPI自动生成
- **容器化**: Docker + Docker Compose
- **CI/CD**: GitHub Actions

## 📁 项目结构

```
august-lab/
├── frontend/                    # 前端项目
│   ├── src/
│   │   ├── frontend/           # 前台展示系统
│   │   │   ├── pages/          # 页面组件
│   │   │   ├── components/     # 前台组件
│   │   │   │   └── product/    # 产品相关组件
│   │   │   ├── layouts/        # 布局组件
│   │   │   ├── composables/    # 组合式函数
│   │   │   └── router/         # 前台路由
│   │   ├── admin/              # 后台管理系统
│   │   │   ├── pages/          # 管理页面
│   │   │   ├── components/     # 管理组件
│   │   │   │   ├── product/    # 产品管理组件
│   │   │   │   ├── analytics/  # 分析组件
│   │   │   │   ├── monitoring/ # 监控组件
│   │   │   │   └── feedback/   # 反馈组件
│   │   │   └── router/         # 后台路由
│   │   └── shared/             # 共享资源
│   │       ├── api.ts          # API服务
│   │       ├── types.ts        # 类型定义
│   │       ├── components/     # 共享组件
│   │       └── composables/    # 组合式函数
│   ├── tests/                  # 属性测试 (Python + Hypothesis)
│   └── dist/                   # 构建输出
├── backend/                     # 后端API
│   ├── app/
│   │   ├── routers/            # API路由
│   │   │   └── products.py     # 产品API路由
│   │   ├── models.py           # 数据模型
│   │   ├── schemas.py          # Pydantic模式
│   │   ├── database.py         # 数据库配置
│   │   ├── security.py         # 安全相关
│   │   └── services/           # 业务服务
│   │       └── product_file_service.py
│   ├── tests/                  # 后端测试
│   ├── uploads/                # 文件上传目录
│   └── products/               # 产品文件存储
├── .kiro/specs/                # 规范文档
│   ├── personal-website/       # 个人网站规范
│   │   ├── requirements.md     # 需求文档
│   │   ├── design.md          # 设计文档
│   │   └── tasks.md           # 实现计划
│   └── product-integration/    # 产品集成规范
│       ├── requirements.md     # 产品需求文档
│       ├── design.md          # 产品设计文档
│       └── tasks.md           # 产品实现计划
├── scripts/                    # 开发脚本
│   ├── dev.bat                # Windows启动脚本
│   ├── dev.sh                 # Linux/Mac启动脚本
│   ├── backup.sh              # Linux/Mac备份脚本
│   ├── backup.bat             # Windows备份脚本
│   └── production-setup.sh    # 生产环境安装脚本
├── Dockerfile                  # Docker镜像构建文件
├── docker-compose.yml         # Docker Compose配置
├── env.example                 # 环境变量配置示例
└── DEPLOYMENT_CHECKLIST.md    # 部署前检查清单
```

## 🚀 快速开始

### 环境要求
- Node.js 18+ 
- Python 3.8+
- Git

### 一键启动（推荐）

**Windows:**
```bash
# 首次运行，安装依赖
scripts\dev.bat --install

# 日常开发
scripts\dev.bat
```

**Linux/Mac:**
```bash
# 首次运行，安装依赖
chmod +x scripts/dev.sh
./scripts/dev.sh --install

# 日常开发
./scripts/dev.sh
```

### 手动启动

#### 1. 克隆项目
```bash
git clone <repository-url>
cd august-lab
```

#### 2. 启动后端
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```

#### 3. 启动前端
```bash
cd frontend
npm install
npm run dev
```

### 访问地址
- **前台网站**: http://localhost:3000
- **产品体验**: http://localhost:3000/product/{id}
- **后台管理**: http://localhost:3000/admin
- **产品管理**: http://localhost:3000/admin/products
- **API接口**: http://localhost:8001
- **API文档**: http://localhost:8001/docs
- **健康检查**: http://localhost:8001/health
- **产品文件**: http://localhost:8001/products/{id}/

### 🔑 默认登录信息
- **用户名**: `admin`
- **密码**: `admin123`

> ⚠️ **安全提示**: 这是演示用的默认凭据，生产环境请务必通过环境变量修改！

### Docker 部署（推荐）

使用 Docker Compose 一键启动所有服务：

```bash
# 配置环境变量
cp env.example .env
# 编辑 .env 文件，填写实际配置

# 启动所有服务（后端、数据库、Nginx）
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

> SQLite 数据文件会保存在项目根目录的 `./data/august_lab.db` 中。

### 生产环境部署

详细的生产环境部署指南请参考：
- 📖 [部署文档](docs/DEPLOYMENT.md) - 完整的部署步骤和配置说明
- ✅ [部署检查清单](DEPLOYMENT_CHECKLIST.md) - 部署前检查项
- 🚀 [生产环境安装脚本](scripts/production-setup.sh) - 自动化安装脚本

## 🧪 测试

### 运行前端测试
```bash
cd frontend
npm run test
```

### 运行属性测试
```bash
cd frontend/tests
python -m pytest -v
```

### 运行后端测试
```bash
cd backend
python -m pytest tests/ -v

# 带覆盖率报告
python -m pytest tests/ -v --cov=app --cov-report=html
```

### 数据库管理
```bash
# 初始化数据库（包含示例数据）
python backend/manage_db.py init

# 仅创建表结构
python backend/manage_db.py create

# 查看数据库统计
python backend/manage_db.py stats

# 运行数据库迁移
python backend/manage_db.py migrate
```

### 产品管理
```bash
# 列出所有产品
python backend/manage_products.py list

# 清理孤立的产品文件
python backend/manage_products.py cleanup
```

### 备份
```bash
# Linux/Mac
./scripts/backup.sh

# Windows
scripts\backup.bat
```

### 测试覆盖率
- **总测试数**: 160+个
- **通过率**: 95%+
- **测试类型**: 单元测试 + 属性测试 + 集成测试 + 产品功能测试

## 📖 开发文档

### 规范驱动开发
本项目采用规范驱动开发方法，包含完整的开发文档：

#### 个人网站规范
- **需求文档** (`.kiro/specs/personal-website/requirements.md`)
  - 使用EARS模式编写的功能需求
  - INCOSE质量标准验证
  - 完整的验收标准

- **设计文档** (`.kiro/specs/personal-website/design.md`)
  - 系统架构设计
  - 数据模型设计
  - 20个正确性属性定义
  - 错误处理策略

- **实现计划** (`.kiro/specs/personal-website/tasks.md`)
  - 11个主要任务模块
  - 40+个具体实现任务
  - 属性测试任务规划

#### 产品集成规范
- **需求文档** (`.kiro/specs/product-integration/requirements.md`)
  - 产品嵌入功能需求
  - 8个主要用户故事
  - 安全性和扩展性要求

- **设计文档** (`.kiro/specs/product-integration/design.md`)
  - 产品容器架构设计
  - 15个正确性属性定义
  - 产品类型支持和API设计

- **实现计划** (`.kiro/specs/product-integration/tasks.md`)
  - 11个主要功能模块
  - 60+个具体实现任务
  - 产品功能测试规划

### API文档
- 自动生成的API文档：http://localhost:8001/docs
- 支持在线测试和调试
- 完整的请求/响应示例

### 属性测试
项目使用属性测试确保代码正确性：
- **数据验证属性**: 确保输入验证的一致性
- **往返一致性**: 验证序列化/反序列化
- **业务逻辑属性**: 验证核心业务规则
- **UI交互属性**: 验证用户界面行为
- **产品隔离属性**: 验证产品间的安全隔离
- **文件完整性属性**: 验证产品文件上传和存储
- **API安全属性**: 验证产品API通信安全性

## 🔧 配置说明

### 环境变量配置

项目使用环境变量管理配置。首次部署前，请复制 `env.example` 为 `.env` 并填写实际值：

```bash
# 复制环境变量示例文件
cp env.example .env

# 编辑配置文件
# Windows: notepad .env
# Linux/Mac: nano .env
```

**重要配置项：**
- `SECRET_KEY` - 生产环境必须修改！使用 `openssl rand -base64 64` 生成
- `ADMIN_USERNAME` / `ADMIN_PASSWORD` - 生产环境必须修改默认凭据
- `DATABASE_URL` - 使用 SQLite 数据库（默认配置）
- `ALLOWED_ORIGINS` - 生产环境必须限制为实际域名

详细配置说明请参考 `env.example` 文件中的注释。

### 数据库
- 使用 SQLite 作为数据库
- 自动创建表结构和示例数据
- 支持数据迁移和备份
- 使用 `python backend/manage_db.py` 进行数据库管理操作

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

### 开发规范
- 遵循TypeScript/Python代码规范
- 编写属性测试验证功能正确性
- 更新相关文档
- 确保所有测试通过

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [Vue.js](https://vuejs.org/) - 渐进式JavaScript框架
- [FastAPI](https://fastapi.tiangolo.com/) - 现代Python Web框架
- [Tailwind CSS](https://tailwindcss.com/) - 实用优先的CSS框架
- [Element Plus](https://element-plus.org/) - Vue 3组件库
- [Hypothesis](https://hypothesis.readthedocs.io/) - 属性测试库

---

**August.Lab** - 用现代技术栈构建的个人网站解决方案 ✨
## 🚀 产品功能详解

### 产品类型支持
- **静态Web应用** - HTML/CSS/JavaScript静态文件
- **单页应用(SPA)** - React、Vue、Angular等框架应用
- **Web游戏** - Canvas、WebGL游戏应用
- **在线工具** - 计算器、编辑器等实用工具

### 产品管理流程
1. **上传产品** - 支持ZIP文件上传，自动解压和验证
2. **配置产品** - 设置产品信息、技术栈和运行参数
3. **预览测试** - 发布前的产品预览和功能测试
4. **发布产品** - 控制产品在前台的可见性
5. **监控分析** - 实时监控产品使用情况和性能

### 安全特性
- **沙箱隔离** - 使用iframe技术确保产品间完全隔离
- **文件验证** - 上传文件的安全扫描和完整性检查
- **API认证** - 基于令牌的产品API访问控制
- **权限管理** - 细粒度的产品操作权限控制
- **错误隔离** - 产品错误不影响主网站运行

### 数据管理
- **专用存储** - 每个产品拥有独立的数据存储空间
- **数据隔离** - 产品间数据完全隔离，确保安全性
- **备份恢复** - 支持产品数据的导出和导入
- **配额管理** - 存储空间配额限制和使用监控

### 用户体验
- **无缝集成** - 产品在个人网站内直接运行，无需跳转
- **响应式设计** - 产品容器适配不同设备屏幕
- **状态保存** - 用户会话状态的保存和恢复
- **个性化设置** - 产品内用户偏好和配置管理

## 🎯 使用场景

### 个人开发者
- 展示个人项目作品和技术能力
- 提供在线工具和实用应用
- 建立个人技术品牌和影响力

### 创业团队
- 产品原型展示和用户测试
- MVP快速验证和迭代
- 统一的产品展示平台

### 教育机构
- 在线教学工具和演示
- 学生作品展示平台
- 交互式学习资源

### 企业应用
- 内部工具和应用展示
- 客户演示和产品试用
- 技术方案展示平台

## 🔮 未来规划

### 短期目标 (v2.0)
- [ ] 产品版本管理和回滚
- [ ] 更多产品类型支持 (PWA、WebAssembly)
- [ ] 产品协作和团队管理
- [ ] 高级分析和报表功能

### 中期目标 (v3.0)
- [x] 自动化部署和CI/CD - ✅ 已完成
- [ ] 产品市场和分享功能
- [ ] 第三方集成 (GitHub、Docker)
- [ ] 多语言和国际化支持

### 长期目标 (v4.0)
- [ ] 云端部署和扩展
- [ ] 企业级功能和权限
- [ ] 插件生态系统
- [ ] AI辅助开发工具

---

**August.Lab** - 不仅是个人网站，更是完整的产品展示和体验平台 🚀✨

##