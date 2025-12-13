# 产品开发和使用指南

本指南详细介绍如何在August.Lab平台上开发、上传、管理和使用产品应用。

## 📋 目录

- [产品概述](#产品概述)
- [支持的产品类型](#支持的产品类型)
- [产品开发指南](#产品开发指南)
- [产品上传流程](#产品上传流程)
- [产品管理](#产品管理)
- [API集成](#api集成)
- [用户系统集成](#用户系统集成)
- [最佳实践](#最佳实践)
- [故障排除](#故障排除)

## 产品概述

August.Lab的产品功能允许您在个人网站内直接嵌入和展示完整的Web应用程序。访客可以在不离开您网站的情况下体验您的产品，提供无缝的用户体验。

### 核心特性

- **安全隔离**: 使用iframe沙箱技术确保产品间完全隔离
- **多类型支持**: 支持静态网站、SPA应用、游戏、工具等
- **数据存储**: 每个产品拥有独立的数据存储空间
- **用户系统**: 产品内用户认证和个性化设置
- **实时监控**: 使用统计、性能监控和错误日志
- **API通信**: 安全的产品与后端通信机制

## 支持的产品类型

### 1. 静态Web应用 (static)

适用于纯HTML/CSS/JavaScript开发的应用。

**文件结构要求:**
```
product.zip
├── index.html          # 入口文件 (必需)
├── css/
│   └── style.css
├── js/
│   └── app.js
└── assets/
    └── images/
```

**配置示例:**
```json
{
  "product_type": "static",
  "entry_file": "index.html",
  "config_data": {
    "title": "我的静态应用",
    "description": "一个简单的静态Web应用"
  }
}
```

### 2. 单页应用 (spa)

适用于React、Vue、Angular等框架开发的应用。

**文件结构要求:**
```
product.zip
├── index.html          # 入口文件 (必需)
├── static/
│   ├── css/
│   ├── js/
│   └── media/
└── manifest.json       # 可选
```

**配置示例:**
```json
{
  "product_type": "spa",
  "entry_file": "index.html",
  "config_data": {
    "framework": "react",
    "version": "18.0.0",
    "routing": "hash"
  }
}
```

### 3. Web游戏 (game)

适用于Canvas、WebGL或游戏引擎开发的游戏。

**文件结构要求:**
```
product.zip
├── index.html          # 入口文件 (必需)
├── game/
│   ├── engine.js
│   ├── assets/
│   └── levels/
└── config.json
```

**配置示例:**
```json
{
  "product_type": "game",
  "entry_file": "index.html",
  "config_data": {
    "engine": "phaser",
    "fullscreen": true,
    "controls": ["keyboard", "mouse"]
  }
}
```

### 4. 在线工具 (tool)

适用于计算器、编辑器等实用工具。

**文件结构要求:**
```
product.zip
├── index.html          # 入口文件 (必需)
├── tool/
│   ├── calculator.js
│   └── utils.js
└── help/
    └── manual.html
```

**配置示例:**
```json
{
  "product_type": "tool",
  "entry_file": "index.html",
  "config_data": {
    "category": "utility",
    "features": ["calculation", "history", "export"]
  }
}
```

## 产品开发指南

### 开发环境准备

1. **本地开发服务器**
   ```bash
   # 使用Python
   python -m http.server 8080
   
   # 使用Node.js
   npx serve .
   
   # 使用Live Server (VS Code扩展)
   ```

2. **跨域处理**
   
   由于产品将在iframe中运行，需要注意跨域问题：
   ```javascript
   // 允许在iframe中运行
   if (window.self !== window.top) {
     // 在iframe中的逻辑
   }
   ```

3. **响应式设计**
   
   确保产品在不同尺寸的容器中正常显示：
   ```css
   /* 响应式容器 */
   .app-container {
     width: 100%;
     height: 100vh;
     min-height: 400px;
   }
   
   @media (max-width: 768px) {
     .app-container {
       min-height: 300px;
     }
   }
   ```

### 与平台集成

#### 1. 获取产品信息

```javascript
// 从URL参数获取产品ID
const urlParams = new URLSearchParams(window.location.search);
const productId = urlParams.get('productId');

// 或从父窗口获取
if (window.parent !== window) {
  window.parent.postMessage({
    type: 'GET_PRODUCT_INFO'
  }, '*');
}
```

#### 2. 用户认证集成

```javascript
// 检查用户登录状态
async function checkUserAuth() {
  try {
    const response = await fetch(`/api/products/${productId}/auth/status`, {
      credentials: 'include'
    });
    const data = await response.json();
    return data.authenticated;
  } catch (error) {
    console.error('Auth check failed:', error);
    return false;
  }
}

// 创建访客会话
async function createGuestSession() {
  try {
    const response = await fetch(`/api/products/${productId}/auth/guest-session`, {
      method: 'POST',
      credentials: 'include'
    });
    const session = await response.json();
    return session;
  } catch (error) {
    console.error('Guest session creation failed:', error);
    return null;
  }
}
```

#### 3. 数据存储

```javascript
// 存储数据
async function saveData(key, data) {
  try {
    const response = await fetch(`/api/products/${productId}/data/${key}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiToken}`
      },
      body: JSON.stringify(data)
    });
    return await response.json();
  } catch (error) {
    console.error('Save data failed:', error);
    return null;
  }
}

// 读取数据
async function loadData(key) {
  try {
    const response = await fetch(`/api/products/${productId}/data/${key}`, {
      headers: {
        'Authorization': `Bearer ${apiToken}`
      }
    });
    const result = await response.json();
    return result.data;
  } catch (error) {
    console.error('Load data failed:', error);
    return null;
  }
}
```

#### 4. 错误报告

```javascript
// 错误报告
function reportError(error, context = {}) {
  fetch(`/api/products/${productId}/logs`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      log_type: 'error',
      log_level: 'error',
      message: error.message,
      details: {
        stack: error.stack,
        context: context,
        timestamp: new Date().toISOString()
      }
    })
  }).catch(console.error);
}

// 全局错误处理
window.addEventListener('error', (event) => {
  reportError(event.error, {
    filename: event.filename,
    lineno: event.lineno,
    colno: event.colno
  });
});
```

## 产品上传流程

### 1. 准备产品文件

1. **创建ZIP包**
   ```bash
   # 确保包含入口文件
   zip -r my-product.zip . -x "*.git*" "node_modules/*" "*.DS_Store"
   ```

2. **文件大小限制**
   - 单个ZIP文件: 最大100MB
   - 解压后总大小: 最大200MB
   - 单个文件: 最大10MB

3. **文件类型限制**
   - 允许: `.html`, `.css`, `.js`, `.json`, `.png`, `.jpg`, `.gif`, `.svg`, `.woff`, `.woff2`
   - 禁止: `.exe`, `.php`, `.asp`, `.jsp` 等服务器端文件

### 2. 后台上传步骤

1. **登录管理后台**
   ```
   访问: http://localhost:3000/admin
   用户名: admin
   密码: admin123
   ```

2. **创建产品**
   - 进入"产品管理"页面
   - 点击"添加产品"
   - 填写基本信息

3. **上传文件**
   - 选择产品ZIP文件
   - 等待上传和解压完成
   - 验证文件完整性

4. **配置产品**
   - 设置产品类型和入口文件
   - 配置运行参数
   - 设置访问权限

5. **预览测试**
   - 使用预览功能测试产品
   - 检查功能是否正常
   - 验证响应式设计

6. **发布产品**
   - 确认无误后发布
   - 产品将在前台可见

### 3. API上传 (高级)

```javascript
// 使用API上传产品
async function uploadProduct(file, productData) {
  // 1. 创建产品
  const productResponse = await fetch('/api/products', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${adminToken}`
    },
    body: JSON.stringify(productData)
  });
  
  const product = await productResponse.json();
  
  // 2. 上传文件
  const formData = new FormData();
  formData.append('file', file);
  
  const uploadResponse = await fetch(`/api/products/${product.id}/upload`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${adminToken}`
    },
    body: formData
  });
  
  return await uploadResponse.json();
}
```

## 产品管理

### 版本管理

```javascript
// 更新产品版本
async function updateProductVersion(productId, version, changelog) {
  const response = await fetch(`/api/products/${productId}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${adminToken}`
    },
    body: JSON.stringify({
      version: version,
      config_data: {
        changelog: changelog
      }
    })
  });
  
  return await response.json();
}
```

### 发布控制

```javascript
// 发布/下线产品
async function toggleProductPublication(productId, isPublished) {
  const response = await fetch(`/api/products/${productId}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${adminToken}`
    },
    body: JSON.stringify({
      is_published: isPublished
    })
  });
  
  return await response.json();
}
```

### 使用统计

```javascript
// 获取产品分析数据
async function getProductAnalytics(productId) {
  const response = await fetch(`/api/products/${productId}/analytics`, {
    headers: {
      'Authorization': `Bearer ${adminToken}`
    }
  });
  
  return await response.json();
}
```

## API集成

### 令牌管理

1. **生成API令牌**
   ```javascript
   const response = await fetch(`/api/products/${productId}/api/token`, {
     method: 'POST',
     headers: {
       'Content-Type': 'application/json',
       'Authorization': `Bearer ${adminToken}`
     },
     body: JSON.stringify({
       permissions: ['read', 'write']
     })
   });
   
   const tokenData = await response.json();
   ```

2. **使用API令牌**
   ```javascript
   const response = await fetch(`/api/products/${productId}/api/proxy/data`, {
     method: 'GET',
     headers: {
       'Authorization': `Bearer ${apiToken}`
     }
   });
   ```

### 安全通信

```javascript
// 安全的API调用封装
class ProductAPI {
  constructor(productId, token) {
    this.productId = productId;
    this.token = token;
    this.baseUrl = `/api/products/${productId}/api/proxy`;
  }
  
  async call(endpoint, options = {}) {
    const url = `${this.baseUrl}/${endpoint}`;
    const config = {
      ...options,
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json',
        ...options.headers
      }
    };
    
    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        throw new Error(`API call failed: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('API call error:', error);
      throw error;
    }
  }
  
  async get(endpoint) {
    return this.call(endpoint, { method: 'GET' });
  }
  
  async post(endpoint, data) {
    return this.call(endpoint, {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }
}
```

## 用户系统集成

### 用户认证

```javascript
// 用户登录
async function loginUser(credentials) {
  const response = await fetch(`/api/products/${productId}/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(credentials)
  });
  
  const result = await response.json();
  
  if (result.user) {
    // 保存用户信息
    localStorage.setItem('user', JSON.stringify(result.user));
    localStorage.setItem('session', JSON.stringify(result.session));
  }
  
  return result;
}

// 用户注册
async function registerUser(userData) {
  const response = await fetch(`/api/products/${productId}/auth/register`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(userData)
  });
  
  return await response.json();
}
```

### 会话管理

```javascript
// 会话恢复
async function restoreSession() {
  const storedSession = localStorage.getItem('session');
  
  if (!storedSession) {
    return false;
  }
  
  const session = JSON.parse(storedSession);
  
  const response = await fetch(`/api/products/${productId}/auth/validate-session`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      session_id: session.id
    })
  });
  
  const result = await response.json();
  return result.valid;
}

// 会话数据同步
async function syncSessionData(data) {
  const session = JSON.parse(localStorage.getItem('session'));
  
  const response = await fetch(`/api/products/${productId}/auth/session-data`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      session_id: session.id,
      session_data: data
    })
  });
  
  return await response.json();
}
```

## 最佳实践

### 性能优化

1. **资源优化**
   ```javascript
   // 懒加载图片
   const images = document.querySelectorAll('img[data-src]');
   const imageObserver = new IntersectionObserver((entries) => {
     entries.forEach(entry => {
       if (entry.isIntersecting) {
         const img = entry.target;
         img.src = img.dataset.src;
         img.removeAttribute('data-src');
         imageObserver.unobserve(img);
       }
     });
   });
   
   images.forEach(img => imageObserver.observe(img));
   ```

2. **缓存策略**
   ```javascript
   // Service Worker缓存
   self.addEventListener('fetch', event => {
     if (event.request.destination === 'image') {
       event.respondWith(
         caches.open('images').then(cache => {
           return cache.match(event.request).then(response => {
             return response || fetch(event.request).then(fetchResponse => {
               cache.put(event.request, fetchResponse.clone());
               return fetchResponse;
             });
           });
         })
       );
     }
   });
   ```

### 错误处理

1. **全局错误捕获**
   ```javascript
   // 未捕获的Promise错误
   window.addEventListener('unhandledrejection', event => {
     reportError(new Error(event.reason), {
       type: 'unhandledrejection'
     });
   });
   
   // 资源加载错误
   window.addEventListener('error', event => {
     if (event.target !== window) {
       reportError(new Error(`Resource load failed: ${event.target.src || event.target.href}`), {
         type: 'resource',
         element: event.target.tagName
       });
     }
   }, true);
   ```

2. **用户友好的错误提示**
   ```javascript
   function showUserError(message, type = 'error') {
     const notification = document.createElement('div');
     notification.className = `notification notification-${type}`;
     notification.textContent = message;
     
     document.body.appendChild(notification);
     
     setTimeout(() => {
       notification.remove();
     }, 5000);
   }
   ```

### 安全考虑

1. **输入验证**
   ```javascript
   function sanitizeInput(input) {
     const div = document.createElement('div');
     div.textContent = input;
     return div.innerHTML;
   }
   
   function validateEmail(email) {
     const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
     return re.test(email);
   }
   ```

2. **XSS防护**
   ```javascript
   // 使用DOMPurify清理HTML
   function safeHTML(html) {
     return DOMPurify.sanitize(html);
   }
   
   // 安全地设置innerHTML
   function setInnerHTML(element, html) {
     element.innerHTML = safeHTML(html);
   }
   ```

## 故障排除

### 常见问题

1. **产品无法加载**
   - 检查入口文件是否存在
   - 验证文件路径是否正确
   - 查看浏览器控制台错误信息

2. **样式显示异常**
   - 检查CSS文件路径
   - 验证相对路径引用
   - 确认字体文件是否正确加载

3. **API调用失败**
   - 验证API令牌是否有效
   - 检查请求URL和参数
   - 查看网络请求状态

4. **用户认证问题**
   - 检查会话是否过期
   - 验证用户权限设置
   - 确认认证流程是否正确

### 调试工具

1. **浏览器开发者工具**
   ```javascript
   // 调试信息输出
   function debug(message, data = null) {
     if (process.env.NODE_ENV === 'development') {
       console.log(`[DEBUG] ${message}`, data);
     }
   }
   ```

2. **性能监控**
   ```javascript
   // 性能测量
   function measurePerformance(name, fn) {
     performance.mark(`${name}-start`);
     const result = fn();
     performance.mark(`${name}-end`);
     performance.measure(name, `${name}-start`, `${name}-end`);
     
     const measure = performance.getEntriesByName(name)[0];
     console.log(`${name} took ${measure.duration}ms`);
     
     return result;
   }
   ```

3. **错误日志**
   ```javascript
   // 详细错误日志
   function logError(error, context) {
     const errorInfo = {
       message: error.message,
       stack: error.stack,
       timestamp: new Date().toISOString(),
       url: window.location.href,
       userAgent: navigator.userAgent,
       context: context
     };
     
     console.error('Error logged:', errorInfo);
     
     // 发送到服务器
     reportError(error, context);
   }
   ```

### 支持资源

- **技术文档**: `/docs/`
- **API参考**: `http://localhost:8000/docs`
- **示例项目**: `/examples/`
- **社区论坛**: [链接]
- **问题反馈**: [GitHub Issues]

---

通过遵循本指南，您可以成功开发、部署和管理在August.Lab平台上的产品应用。如有任何问题，请参考故障排除部分或联系技术支持。