# 需求文档

## 介绍

个人网站是一个全栈Web应用程序，包含前台展示网站和后台管理系统。前台用于展示个人作品、博客文章和个人信息，后台提供内容管理功能。系统采用Vue3 + Element Plus前端框架，FastAPI后端框架，SQLite数据库存储。

## 术语表

- **前台系统 (Frontend_Display)**: 面向访客的展示网站，包含首页、作品、博客、关于我四个主要页面
- **后台系统 (Backend_Admin)**: 管理员专用的内容管理系统，用于管理前台展示内容
- **管理员 (Administrator)**: 网站所有者，唯一有权限访问后台系统的用户
- **访客 (Visitor)**: 浏览前台网站的普通用户
- **作品项目 (Portfolio_Item)**: 在作品页面展示的项目条目
- **博客文章 (Blog_Post)**: 在博客页面展示的文章内容
- **内容管理 (Content_Management)**: 对网站展示内容进行增删改查操作

## 需求

### 需求 1

**用户故事:** 作为访客，我想要浏览一个美观的个人网站前台，命名为“august.lab”，以便了解网站所有者的信息和作品。

#### 验收标准

1. WHEN 访客访问网站首页 THEN Frontend_Display SHALL 展示包含导航菜单、个人介绍和最新内容预览的首页
2. WHEN 访客点击导航菜单 THEN Frontend_Display SHALL 提供首页、作品、博客、关于我四个页面的导航功能
3. WHEN 访客浏览任意页面 THEN Frontend_Display SHALL 使用自定义CSS样式而非管理后台风格的界面设计
4. WHEN 访客在不同设备上访问 THEN Frontend_Display SHALL 提供响应式布局适配不同屏幕尺寸
5. WHEN 访客浏览页面内容 THEN Frontend_Display SHALL 确保所有文本和图片内容正确加载和显示

### 需求 2

**用户故事:** 作为访客，我想要查看作品展示页面，以便了解网站所有者的项目和技能。

#### 验收标准

1. WHEN 访客访问作品页面 THEN Frontend_Display SHALL 展示所有已发布的Portfolio_Item列表
2. WHEN 访客点击作品项目 THEN Frontend_Display SHALL 显示该Portfolio_Item的详细信息包括标题、描述、技术栈和链接
3. WHEN 作品页面加载 THEN Frontend_Display SHALL 按照发布时间或指定顺序排列Portfolio_Item
4. WHEN 没有作品内容时 THEN Frontend_Display SHALL 显示友好的空状态提示信息
5. WHEN 作品项目包含图片 THEN Frontend_Display SHALL 正确加载和展示项目截图或封面图

### 需求 3

**用户故事:** 作为访客，我想要阅读博客文章，以便了解网站所有者的想法和经验分享。

#### 验收标准

1. WHEN 访客访问博客页面 THEN Frontend_Display SHALL 展示所有已发布的Blog_Post列表
2. WHEN 访客点击博客文章 THEN Frontend_Display SHALL 显示完整的Blog_Post内容包括标题、发布时间、正文和标签
3. WHEN 博客页面加载 THEN Frontend_Display SHALL 按照发布时间倒序排列Blog_Post
4. WHEN 博客文章包含Markdown格式 THEN Frontend_Display SHALL 正确解析和渲染Markdown内容
5. WHEN 没有博客内容时 THEN Frontend_Display SHALL 显示友好的空状态提示信息

### 需求 4

**用户故事:** 作为访客，我想要查看关于我页面，以便了解网站所有者的个人信息和联系方式。

#### 验收标准

1. WHEN 访客访问关于我页面 THEN Frontend_Display SHALL 展示个人简介、技能、经历和联系信息
2. WHEN 页面包含个人照片 THEN Frontend_Display SHALL 正确加载和展示个人头像或照片
3. WHEN 页面包含联系方式 THEN Frontend_Display SHALL 提供邮箱、社交媒体等联系链接
4. WHEN 页面包含技能信息 THEN Frontend_Display SHALL 以可视化方式展示技能和熟练程度
5. WHEN 页面内容更新 THEN Frontend_Display SHALL 实时反映最新的个人信息

### 需求 5

**用户故事:** 作为管理员，我想要通过安全的登录系统访问后台，以便管理网站内容。

#### 验收标准

1. WHEN Administrator 访问后台登录页面 THEN Backend_Admin SHALL 提供用户名和密码输入表单
2. WHEN Administrator 输入正确的预设用户名和密码 THEN Backend_Admin SHALL 验证凭据并允许访问管理界面
3. WHEN Administrator 输入错误的凭据 THEN Backend_Admin SHALL 拒绝访问并显示错误提示信息
4. WHEN Administrator 成功登录 THEN Backend_Admin SHALL 创建会话并重定向到管理主页
5. WHEN Administrator 会话过期或主动登出 THEN Backend_Admin SHALL 清除会话并重定向到登录页面

### 需求 6

**用户故事:** 作为管理员，我想要在后台管理作品项目，以便维护前台作品展示内容。

#### 验收标准

1. WHEN Administrator 访问作品管理页面 THEN Backend_Admin SHALL 显示所有Portfolio_Item的列表和管理操作
2. WHEN Administrator 创建新作品项目 THEN Backend_Admin SHALL 提供表单输入标题、描述、技术栈、链接和图片
3. WHEN Administrator 编辑现有Portfolio_Item THEN Backend_Admin SHALL 加载当前数据并允许修改所有字段
4. WHEN Administrator 删除Portfolio_Item THEN Backend_Admin SHALL 确认操作并从数据库中移除该项目
5. WHEN Administrator 保存Portfolio_Item THEN Backend_Admin SHALL 验证数据完整性并持久化到SQLite数据库

### 需求 7

**用户故事:** 作为管理员，我想要在后台管理博客文章，以便维护前台博客内容。

#### 验收标准

1. WHEN Administrator 访问博客管理页面 THEN Backend_Admin SHALL 显示所有Blog_Post的列表和管理操作
2. WHEN Administrator 创建新博客文章 THEN Backend_Admin SHALL 提供表单输入标题、内容、标签和发布状态
3. WHEN Administrator 编辑现有Blog_Post THEN Backend_Admin SHALL 加载当前数据并支持Markdown编辑器
4. WHEN Administrator 删除Blog_Post THEN Backend_Admin SHALL 确认操作并从数据库中移除该文章
5. WHEN Administrator 保存Blog_Post THEN Backend_Admin SHALL 验证数据完整性并持久化到SQLite数据库

### 需求 8

**用户故事:** 作为管理员，我想要在后台管理个人信息，以便更新前台关于我页面的内容。

#### 验收标准

1. WHEN Administrator 访问个人信息管理页面 THEN Backend_Admin SHALL 显示当前个人信息和编辑表单
2. WHEN Administrator 更新个人简介 THEN Backend_Admin SHALL 提供富文本编辑器支持格式化内容
3. WHEN Administrator 上传个人照片 THEN Backend_Admin SHALL 处理图片文件并更新头像显示
4. WHEN Administrator 修改联系信息 THEN Backend_Admin SHALL 验证邮箱格式和链接有效性
5. WHEN Administrator 保存个人信息 THEN Backend_Admin SHALL 立即更新前台关于我页面的显示内容

### 需求 9

**用户故事:** 作为开发者，我想要系统具有可靠的数据持久化，以便确保内容不会丢失。

#### 验收标准

1. WHEN 系统启动时 THEN 后端系统 SHALL 初始化SQLite数据库并创建必要的数据表结构
2. WHEN 执行数据库操作时 THEN 后端系统 SHALL 使用事务确保数据一致性和完整性
3. WHEN 数据库连接失败时 THEN 后端系统 SHALL 记录错误并提供友好的错误响应
4. WHEN 进行数据备份时 THEN 后端系统 SHALL 支持SQLite数据库文件的导出和恢复
5. WHEN 数据库查询执行时 THEN 后端系统 SHALL 使用参数化查询防止SQL注入攻击

### 需求 10

**用户故事:** 作为开发者，我想要系统具有良好的API设计，以便前后端能够高效通信。

#### 验收标准

1. WHEN 前端请求API时 THEN 后端系统 SHALL 提供RESTful API接口支持CRUD操作
2. WHEN API返回数据时 THEN 后端系统 SHALL 使用JSON格式并包含适当的HTTP状态码
3. WHEN API接收请求时 THEN 后端系统 SHALL 验证请求参数和数据格式的有效性
4. WHEN 发生API错误时 THEN 后端系统 SHALL 返回结构化的错误信息和错误代码
5. WHEN 处理文件上传时 THEN 后端系统 SHALL 支持图片文件的上传、存储和访问功能