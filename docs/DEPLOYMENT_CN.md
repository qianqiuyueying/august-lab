# August.Lab 服务器部署指南

本指南提供两种部署方式：**Docker 部署**（推荐）和**传统部署**。

## 📋 目录

- [方式一：Docker 部署（推荐）](#方式一docker-部署推荐)
- [方式二：传统部署](#方式二传统部署)
- [部署后配置](#部署后配置)
- [常见问题](#常见问题)

---

## 方式一：Docker 部署（推荐）

Docker 部署是最简单的方式，适合快速部署和迁移。

### 前置要求

- 服务器已安装 Docker 和 Docker Compose
- 服务器有至少 2GB 内存和 20GB 磁盘空间
- 已配置域名（可选，用于 HTTPS）

### 步骤 1：准备服务器

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装 Docker（如果未安装）
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 安装 Docker Compose（如果未安装）
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 步骤 2：上传项目代码

```bash
# 方式 A：使用 Git 克隆
cd /opt
sudo git clone https://github.com/your-username/august-lab.git
cd august-lab

# 方式 B：使用 SCP 上传
# 在本地执行：scp -r ./August user@server:/opt/august-lab
```

### 步骤 3：配置环境变量

```bash
# 复制环境变量示例文件
cp env.example .env

# 编辑环境变量（必须修改以下内容）
nano .env
```

**必须修改的配置项：**

```bash
# 生成安全的 SECRET_KEY
SECRET_KEY=$(openssl rand -base64 64)

# 修改管理员密码
ADMIN_USERNAME=admin
ADMIN_PASSWORD=你的强密码

# 配置域名（如果有）
DOMAIN=your-domain.com
FRONTEND_URL=https://your-domain.com
API_URL=https://your-domain.com/api
ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com
```

### 步骤 4：启动服务

```bash
# 构建并启动容器
docker-compose up -d

# 查看日志
docker-compose logs -f

# 检查服务状态
docker-compose ps
```

### 步骤 5：配置 Nginx（可选，用于 HTTPS）

如果需要使用 HTTPS 和自定义域名，需要配置 Nginx 反向代理：

```bash
# 安装 Nginx
sudo apt install -y nginx certbot python3-certbot-nginx

# 创建 Nginx 配置（参考下面的 nginx.conf 配置）
sudo nano /etc/nginx/sites-available/august-lab

# 启用站点
sudo ln -s /etc/nginx/sites-available/august-lab /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# 配置 SSL 证书
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

### 步骤 6：验证部署

```bash
# 检查健康状态
curl http://localhost:8000/health

# 访问前端（如果配置了域名）
# 浏览器打开：https://your-domain.com
```

---

## 方式二：传统部署

传统部署适合需要更多控制或无法使用 Docker 的场景。

### 前置要求

- Ubuntu 20.04+ 或 Debian 11+
- Python 3.8+
- Node.js 18+
- Nginx
- 至少 4GB 内存和 50GB 磁盘空间

### 快速安装（使用自动化脚本）

```bash
# 下载并运行安装脚本
wget https://raw.githubusercontent.com/your-username/august-lab/main/scripts/production-setup.sh
chmod +x production-setup.sh
./production-setup.sh

# 脚本会自动完成：
# - 安装系统依赖
# - 安装 Python 和 Node.js
# - 配置 Nginx
# - 创建系统服务
# - 设置备份和监控
```

### 手动安装步骤

#### 1. 安装系统依赖

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv nodejs npm nginx git
```

#### 2. 克隆项目

```bash
cd /var/www
sudo git clone https://github.com/your-username/august-lab.git
sudo chown -R $USER:$USER august-lab
cd august-lab
```

#### 3. 配置后端

```bash
# 创建虚拟环境
cd backend
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp ../env.example ../.env
nano ../.env  # 修改必要的配置

# 初始化数据库
python manage_db.py
```

#### 4. 构建前端

```bash
cd ../frontend
npm install
npm run build
```

#### 5. 配置 Nginx

```bash
# 创建 Nginx 配置
sudo nano /etc/nginx/sites-available/august-lab
```

参考下面的 Nginx 配置示例。

#### 6. 创建系统服务

```bash
# 创建 systemd 服务文件
sudo nano /etc/systemd/system/august-lab.service
```

服务配置示例：

```ini
[Unit]
Description=August.Lab API Server
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/var/www/august-lab/backend
Environment="PATH=/var/www/august-lab/backend/venv/bin"
EnvironmentFile=/var/www/august-lab/.env
ExecStart=/var/www/august-lab/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

```bash
# 启用并启动服务
sudo systemctl daemon-reload
sudo systemctl enable august-lab
sudo systemctl start august-lab
sudo systemctl status august-lab
```

---

## 部署后配置

### 1. 配置防火墙

```bash
# Ubuntu/Debian
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# 如果使用 Docker，还需要允许 Docker 端口
sudo ufw allow 8000/tcp
```

### 2. 配置 SSL 证书（Let's Encrypt）

```bash
# 安装 Certbot
sudo apt install -y certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# 设置自动续期
sudo certbot renew --dry-run
```

### 3. 配置自动备份

项目已包含备份脚本，设置定时任务：

```bash
# 编辑 crontab
crontab -e

# 添加以下内容（每天凌晨 2 点备份数据库）
0 2 * * * /usr/local/bin/august-lab-backup-db.sh

# 添加以下内容（每天凌晨 3 点备份文件）
0 3 * * * /usr/local/bin/august-lab-backup-files.sh
```

### 4. 配置监控

```bash
# 查看服务状态
sudo systemctl status august-lab

# 查看日志
sudo journalctl -u august-lab -f

# 查看应用日志（如果配置了）
tail -f /var/log/august-lab/app.log
```

---

## Nginx 配置示例

创建文件 `/etc/nginx/sites-available/august-lab`：

```nginx
# HTTP 重定向到 HTTPS
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS 配置
server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    # SSL 证书（Certbot 会自动配置）
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    # SSL 安全配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # 安全头
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;

    # 前端静态文件
    root /var/www/august-lab/frontend/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
        
        # 静态资源缓存
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # API 代理（Docker 部署）
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 文件上传大小限制
        client_max_body_size 100M;
        
        # WebSocket 支持（如果需要）
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # 产品文件服务
    location /products/ {
        alias /var/www/august-lab/backend/products/;
        expires 1h;
        add_header Cache-Control "public";
    }

    # 上传文件服务
    location /uploads/ {
        alias /var/www/august-lab/backend/uploads/;
        expires 1y;
        add_header Cache-Control "public";
    }
}
```

---

## 常见问题

### 1. 服务无法启动

```bash
# 检查服务状态
sudo systemctl status august-lab

# 查看详细日志
sudo journalctl -u august-lab -n 50

# 检查端口占用
sudo netstat -tlnp | grep 8000
```

### 2. 数据库连接失败

```bash
# 检查数据库文件权限
ls -la /var/www/august-lab/august_lab.db

# 修复权限
sudo chown www-data:www-data /var/www/august-lab/august_lab.db
sudo chmod 600 /var/www/august-lab/august_lab.db
```

### 3. 前端无法访问 API

- 检查 `.env` 中的 `ALLOWED_ORIGINS` 配置
- 检查 Nginx 配置中的 `/api/` 代理设置
- 检查后端服务是否正常运行

### 4. 文件上传失败

```bash
# 检查上传目录权限
ls -la /var/www/august-lab/backend/uploads/

# 修复权限
sudo chown -R www-data:www-data /var/www/august-lab/backend/uploads/
sudo chmod -R 755 /var/www/august-lab/backend/uploads/
```

### 5. Docker 容器无法启动

```bash
# 查看容器日志
docker-compose logs backend

# 检查环境变量
docker-compose config

# 重启容器
docker-compose restart
```

---

## 更新部署

### Docker 方式

```bash
cd /opt/august-lab
git pull
docker-compose build
docker-compose up -d
```

### 传统方式

```bash
cd /var/www/august-lab
git pull
cd backend
source venv/bin/activate
pip install -r requirements.txt
python manage_db.py  # 如果有数据库迁移
cd ../frontend
npm install
npm run build
sudo systemctl restart august-lab
sudo systemctl reload nginx
```

---

## 性能优化建议

1. **数据库优化**：定期执行 `VACUUM` 命令优化 SQLite 数据库
2. **缓存配置**：考虑使用 Redis 进行缓存（需要修改代码）
3. **CDN 配置**：将静态资源部署到 CDN
4. **负载均衡**：高并发场景下使用多实例 + 负载均衡器

---

## 安全建议

1. ✅ 修改默认管理员密码
2. ✅ 使用强 SECRET_KEY
3. ✅ 启用 HTTPS
4. ✅ 配置防火墙规则
5. ✅ 定期更新系统和依赖
6. ✅ 配置自动备份
7. ✅ 监控日志和异常

---

## 获取帮助

- 查看详细文档：`docs/DEPLOYMENT.md`
- 查看部署检查清单：`DEPLOYMENT_CHECKLIST.md`
- 提交 Issue：GitHub Issues

---

**祝部署顺利！** 🚀

