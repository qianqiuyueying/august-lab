# 生产环境部署指南

本指南详细介绍如何将August.Lab部署到生产环境，包括安全配置、性能优化和监控设置。

## 📋 目录

- [部署架构](#部署架构)
- [环境准备](#环境准备)
- [安全配置](#安全配置)
- [性能优化](#性能优化)
- [监控和日志](#监控和日志)
- [备份策略](#备份策略)
- [故障排除](#故障排除)

## 部署架构

### 推荐架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Load Balancer │    │   Web Server    │    │   Database      │
│   (Nginx/HAProxy)│────│   (Nginx)       │────│   (SQLite)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                       ┌─────────────────┐
                       │   App Server    │
                       │   (FastAPI)     │
                       └─────────────────┘
                                │
                       ┌─────────────────┐
                       │   File Storage  │
                       │   (Local/S3)    │
                       └─────────────────┘
```

### 单服务器部署

```
┌─────────────────────────────────────────────────────────────┐
│                        Server                               │
├─────────────────┬─────────────────┬─────────────────────────┤
│   Nginx         │   FastAPI       │   SQLite                │
│   (Port 80/443) │   (Port 8000)   │   (文件数据库)          │
│                 │                 │                         │
│ - Static Files  │ - API Server    │ - Database             │
│ - Reverse Proxy │ - File Upload   │ - User Data            │
│ - SSL/TLS       │ - Authentication│ - Product Data         │
└─────────────────┴─────────────────┴─────────────────────────┘
```

## 环境准备

### 系统要求

**最低配置:**
- CPU: 2核心
- 内存: 4GB RAM
- 存储: 50GB SSD
- 网络: 100Mbps

**推荐配置:**
- CPU: 4核心
- 内存: 8GB RAM
- 存储: 100GB SSD
- 网络: 1Gbps

### 软件依赖

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3.8 python3-pip nodejs npm nginx

# CentOS/RHEL
sudo yum update
sudo yum install -y python38 python3-pip nodejs npm nginx

# 安装PM2 (进程管理)
npm install -g pm2

# 安装Certbot (SSL证书)
sudo apt install -y certbot python3-certbot-nginx
```

### 环境变量配置

创建生产环境配置文件:

```bash
# /etc/august-lab/.env
# 数据库配置（使用SQLite）
DATABASE_URL=sqlite:///./august_lab.db

# 安全配置
SECRET_KEY=your-super-secret-key-here-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 文件存储
UPLOAD_DIR=/var/lib/august-lab/uploads
PRODUCTS_DIR=/var/lib/august-lab/products
MAX_FILE_SIZE=104857600  # 100MB

# 邮件配置
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# 监控配置
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
LOG_LEVEL=INFO

# 域名配置
DOMAIN=your-domain.com
FRONTEND_URL=https://your-domain.com
API_URL=https://api.your-domain.com
```

## 安全配置

### 1. SSL/TLS配置

```nginx
# /etc/nginx/sites-available/august-lab
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    # SSL配置
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # 安全头
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

    # 前端静态文件
    location / {
        root /var/www/august-lab/frontend/dist;
        try_files $uri $uri/ /index.html;
        
        # 缓存配置
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # API代理
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 文件上传大小限制
        client_max_body_size 100M;
    }

    # 产品文件服务
    location /products/ {
        alias /var/lib/august-lab/products/;
        
        # 安全配置
        add_header X-Frame-Options "SAMEORIGIN";
        add_header Content-Security-Policy "default-src 'self' 'unsafe-inline' 'unsafe-eval' data: blob:";
        
        # 缓存配置
        expires 1h;
        add_header Cache-Control "public";
    }

    # 上传文件服务
    location /uploads/ {
        alias /var/lib/august-lab/uploads/;
        expires 1y;
        add_header Cache-Control "public";
    }
}
```

### 2. 防火墙配置

```bash
# UFW配置
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable

# 或者使用iptables
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT
sudo iptables -A INPUT -j DROP
```

### 3. 数据库安全

项目使用 SQLite 数据库，数据库文件位于项目根目录 `august_lab.db`。

**安全建议：**
- 确保数据库文件权限设置正确（仅应用用户可读写）
- 定期备份数据库文件
- 生产环境建议将数据库文件放在安全目录，并设置适当的文件权限

```bash
# 设置数据库文件权限
chmod 600 august_lab.db
chown august-lab:august-lab august_lab.db
```

### 4. 应用安全配置

```python
# backend/app/config.py
import os
from typing import Optional

class Settings:
    # 安全配置
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-this-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # 数据库
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./august_lab.db")
    
    # 文件上传
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "104857600"))  # 100MB
    ALLOWED_EXTENSIONS: set = {".zip", ".jpg", ".png", ".gif", ".svg"}
    
    # CORS配置
    ALLOWED_ORIGINS: list = [
        "https://your-domain.com",
        "https://www.your-domain.com"
    ]
    
    # 速率限制
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 3600  # 1小时
    
    # 日志配置
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    SENTRY_DSN: Optional[str] = os.getenv("SENTRY_DSN")

settings = Settings()
```

## 性能优化

### 1. 数据库优化

项目使用 SQLite 数据库，索引已在模型定义中自动创建。SQLite 的性能优化建议：

```python
# SQLite 性能优化已在 database.py 中配置：
# - 连接池使用 StaticPool
# - 连接超时设置为 30 秒
# - 连接回收时间设置为 1 小时
# - 连接前预检查 (pool_pre_ping)
```

**SQLite 性能提示：**
- 数据库文件建议放在 SSD 上以提高 I/O 性能
- 定期执行 `VACUUM` 命令优化数据库（可通过 `manage_db.py` 工具）
- 对于高并发场景，考虑使用 WAL 模式（Write-Ahead Logging）

### 2. 应用服务器优化

```python
# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(
    title="August.Lab API",
    description="Personal Website and Product Platform API",
    version="2.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None
)

# 中间件配置
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# 连接池配置
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600
)
```

### 3. 缓存配置

```python
# backend/app/cache.py
import redis
from functools import wraps
import json
import hashlib

redis_client = redis.Redis.from_url(settings.REDIS_URL)

def cache_result(expire_time=3600):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = f"{func.__name__}:{hashlib.md5(str(args + tuple(kwargs.items())).encode()).hexdigest()}"
            
            # 尝试从缓存获取
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            # 执行函数并缓存结果
            result = await func(*args, **kwargs)
            redis_client.setex(cache_key, expire_time, json.dumps(result, default=str))
            
            return result
        return wrapper
    return decorator

# 使用示例
@cache_result(expire_time=1800)  # 30分钟缓存
async def get_product_analytics(product_id: int):
    # 复杂的分析查询
    pass
```

### 4. 前端优化

```javascript
// frontend/vite.config.ts
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['vue', 'vue-router', 'axios'],
          ui: ['element-plus'],
          utils: ['lodash', 'dayjs']
        }
      }
    },
    chunkSizeWarningLimit: 1000
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
```

## 监控和日志

### 1. 应用监控

```python
# backend/app/monitoring.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
import logging
import time
from fastapi import Request

# Sentry配置
if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        integrations=[
            FastApiIntegration(auto_enabling_integrations=False),
            SqlalchemyIntegration(),
        ],
        traces_sample_rate=0.1,
        environment="production"
    )

# 日志配置
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/august-lab/app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# 性能监控中间件
@app.middleware("http")
async def performance_monitoring(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    
    # 记录慢请求
    if process_time > 1.0:
        logger.warning(f"Slow request: {request.method} {request.url} took {process_time:.2f}s")
    
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

### 2. 系统监控

```bash
# 安装监控工具
sudo apt install -y htop iotop nethogs

# 创建监控脚本 /usr/local/bin/august-lab-monitor.sh
#!/bin/bash

LOG_FILE="/var/log/august-lab/system-monitor.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

# 系统资源使用情况
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | awk -F'%' '{print $1}')
MEM_USAGE=$(free | grep Mem | awk '{printf("%.2f", $3/$2 * 100.0)}')
DISK_USAGE=$(df -h / | awk 'NR==2{printf "%s", $5}')

# 应用进程状态
API_PROCESS=$(pgrep -f "uvicorn main:app" | wc -l)
NGINX_PROCESS=$(pgrep nginx | wc -l)
DB_PROCESS=$(pgrep postgres | wc -l)

echo "$DATE - CPU: ${CPU_USAGE}%, MEM: ${MEM_USAGE}%, DISK: ${DISK_USAGE}, API: $API_PROCESS, NGINX: $NGINX_PROCESS, DB: $DB_PROCESS" >> $LOG_FILE

# 检查磁盘空间
DISK_USAGE_NUM=$(echo $DISK_USAGE | sed 's/%//')
if [ $DISK_USAGE_NUM -gt 80 ]; then
    echo "$DATE - WARNING: Disk usage is ${DISK_USAGE}" >> $LOG_FILE
fi

# 检查内存使用
if (( $(echo "$MEM_USAGE > 80" | bc -l) )); then
    echo "$DATE - WARNING: Memory usage is ${MEM_USAGE}%" >> $LOG_FILE
fi
```

```bash
# 添加到crontab
crontab -e
# 每5分钟执行一次监控
*/5 * * * * /usr/local/bin/august-lab-monitor.sh
```

### 3. 日志轮转

```bash
# /etc/logrotate.d/august-lab
/var/log/august-lab/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        systemctl reload nginx
        systemctl restart august-lab
    endscript
}
```

## 备份策略

### 1. 数据库备份

```bash
#!/bin/bash
# /usr/local/bin/backup-database.sh

BACKUP_DIR="/var/backups/august-lab"
DATE=$(date +%Y%m%d_%H%M%S)
DB_FILE="/var/www/august-lab/august_lab.db"

# 创建备份目录
mkdir -p $BACKUP_DIR

# SQLite数据库备份
if [ -f "$DB_FILE" ]; then
    cp "$DB_FILE" "$BACKUP_DIR/db_backup_$DATE.sqlite"
    gzip "$BACKUP_DIR/db_backup_$DATE.sqlite"
    echo "$(date): Database backup completed" >> /var/log/august-lab/backup.log
else
    echo "$(date): ERROR: Database file not found: $DB_FILE" >> /var/log/august-lab/backup.log
fi

# 保留最近30天的备份
find $BACKUP_DIR -name "db_backup_*.sqlite.gz" -mtime +30 -delete

# 上传到云存储 (可选)
# aws s3 cp $BACKUP_DIR/db_backup_$DATE.sqlite.gz s3://your-backup-bucket/database/
```

### 2. 文件备份

```bash
#!/bin/bash
# /usr/local/bin/backup-files.sh

BACKUP_DIR="/var/backups/august-lab"
DATE=$(date +%Y%m%d_%H%M%S)
SOURCE_DIRS="/var/lib/august-lab/uploads /var/lib/august-lab/products"

# 创建备份目录
mkdir -p $BACKUP_DIR

# 文件备份
tar -czf $BACKUP_DIR/files_backup_$DATE.tar.gz $SOURCE_DIRS

# 保留最近7天的文件备份
find $BACKUP_DIR -name "files_backup_*.tar.gz" -mtime +7 -delete

# 上传到云存储 (可选)
# aws s3 cp $BACKUP_DIR/files_backup_$DATE.tar.gz s3://your-backup-bucket/files/
```

### 3. 自动备份配置

```bash
# 添加到crontab
crontab -e

# 每天凌晨2点备份数据库
0 2 * * * /usr/local/bin/backup-database.sh

# 每天凌晨3点备份文件
0 3 * * * /usr/local/bin/backup-files.sh

# 每周日凌晨4点完整备份
0 4 * * 0 /usr/local/bin/full-backup.sh
```

## 部署脚本

### 1. 自动部署脚本

```bash
#!/bin/bash
# deploy.sh

set -e

echo "Starting August.Lab deployment..."

# 配置变量
APP_DIR="/var/www/august-lab"
BACKUP_DIR="/var/backups/august-lab/deploy"
SERVICE_NAME="august-lab"

# 创建备份
echo "Creating backup..."
mkdir -p $BACKUP_DIR
cp -r $APP_DIR $BACKUP_DIR/$(date +%Y%m%d_%H%M%S)

# 拉取最新代码
echo "Pulling latest code..."
cd $APP_DIR
git pull origin main

# 安装后端依赖
echo "Installing backend dependencies..."
cd backend
pip install -r requirements.txt

# 数据库迁移
echo "Running database migrations..."
python manage_db.py

# 构建前端
echo "Building frontend..."
cd ../frontend
npm install
npm run build

# 重启服务
echo "Restarting services..."
sudo systemctl restart $SERVICE_NAME
sudo systemctl restart nginx

# 健康检查
echo "Performing health check..."
sleep 5
if curl -f http://localhost:8000/health; then
    echo "Deployment successful!"
else
    echo "Deployment failed! Rolling back..."
    # 回滚逻辑
    exit 1
fi
```

### 2. 服务配置

```ini
# /etc/systemd/system/august-lab.service
[Unit]
Description=August.Lab API Server
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/var/www/august-lab/backend
Environment=PATH=/var/www/august-lab/venv/bin
EnvironmentFile=/etc/august-lab/.env
ExecStart=/var/www/august-lab/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

```bash
# 启用服务
sudo systemctl daemon-reload
sudo systemctl enable august-lab
sudo systemctl start august-lab
```

## 故障排除

### 常见问题

1. **服务无法启动**
   ```bash
   # 检查服务状态
   sudo systemctl status august-lab
   
   # 查看日志
   sudo journalctl -u august-lab -f
   
   # 检查端口占用
   sudo netstat -tlnp | grep :8000
   ```

2. **数据库连接失败**
   ```bash
   # 检查数据库文件是否存在
   ls -la /var/www/august-lab/august_lab.db
   
   # 检查文件权限
   ls -l august_lab.db
   
   # 修复权限（如果需要）
   sudo chown august-lab:august-lab august_lab.db
   sudo chmod 600 august_lab.db
   
   # 使用管理工具检查数据库
   cd /var/www/august-lab/backend
   python manage_db.py health
   ```

3. **文件上传失败**
   ```bash
   # 检查目录权限
   ls -la /var/lib/august-lab/
   
   # 修复权限
   sudo chown -R www-data:www-data /var/lib/august-lab/
   sudo chmod -R 755 /var/lib/august-lab/
   ```

4. **SSL证书问题**
   ```bash
   # 检查证书状态
   sudo certbot certificates
   
   # 续期证书
   sudo certbot renew --dry-run
   
   # 测试SSL配置
   openssl s_client -connect your-domain.com:443
   ```

### 性能问题诊断

```bash
# 系统资源监控
htop
iotop
nethogs

# 数据库性能（SQLite）
sqlite3 august_lab.db "SELECT COUNT(*) FROM sqlite_master WHERE type='table';"
sqlite3 august_lab.db ".schema" | head -20

# 应用性能
curl -w "@curl-format.txt" -o /dev/null -s "http://localhost:8000/api/products"

# Nginx访问日志分析
sudo tail -f /var/log/nginx/access.log | grep -E "(POST|PUT|DELETE)"
```

### 安全检查

```bash
# 端口扫描
nmap -sS -O localhost

# 文件权限检查
find /var/www/august-lab -type f -perm /o+w

# 日志审计
sudo grep -i "failed\|error\|unauthorized" /var/log/august-lab/app.log

# SSL安全检查
testssl.sh your-domain.com
```

---

通过遵循本部署指南，您可以安全、高效地将August.Lab部署到生产环境。定期检查监控指标和日志，确保系统稳定运行。