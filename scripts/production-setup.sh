#!/bin/bash

# August.Lab 生产环境安装脚本
# 适用于 Ubuntu 20.04+ / Debian 11+

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查是否为root用户
check_root() {
    if [[ $EUID -eq 0 ]]; then
        log_error "请不要使用root用户运行此脚本"
        exit 1
    fi
}

# 检查系统版本
check_system() {
    log_info "检查系统版本..."
    
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        OS=$NAME
        VER=$VERSION_ID
        log_info "检测到系统: $OS $VER"
    else
        log_error "无法检测系统版本"
        exit 1
    fi
    
    # 检查是否为支持的系统
    if [[ "$OS" != *"Ubuntu"* ]] && [[ "$OS" != *"Debian"* ]]; then
        log_warning "此脚本主要针对Ubuntu/Debian系统，其他系统可能需要手动调整"
    fi
}

# 更新系统包
update_system() {
    log_info "更新系统包..."
    sudo apt update
    sudo apt upgrade -y
    log_success "系统包更新完成"
}

# 安装基础依赖
install_dependencies() {
    log_info "安装基础依赖..."
    
    sudo apt install -y \
        curl \
        wget \
        git \
        unzip \
        software-properties-common \
        apt-transport-https \
        ca-certificates \
        gnupg \
        lsb-release \
        build-essential \
        supervisor
    
    log_success "基础依赖安装完成"
}

# 安装Python 3.8+
install_python() {
    log_info "安装Python 3.8+..."
    
    # 检查Python版本
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
        log_info "当前Python版本: $PYTHON_VERSION"
        
        if (( $(echo "$PYTHON_VERSION >= 3.8" | bc -l) )); then
            log_success "Python版本满足要求"
        else
            log_warning "Python版本过低，尝试安装Python 3.8"
            sudo apt install -y python3.8 python3.8-venv python3.8-dev
        fi
    else
        sudo apt install -y python3 python3-venv python3-dev python3-pip
    fi
    
    # 安装pip
    if ! command -v pip3 &> /dev/null; then
        sudo apt install -y python3-pip
    fi
    
    log_success "Python安装完成"
}

# 安装Node.js
install_nodejs() {
    log_info "安装Node.js..."
    
    # 添加NodeSource仓库
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
    sudo apt install -y nodejs
    
    # 验证安装
    NODE_VERSION=$(node --version)
    NPM_VERSION=$(npm --version)
    log_success "Node.js $NODE_VERSION 和 npm $NPM_VERSION 安装完成"
    
    # 安装PM2
    sudo npm install -g pm2
    log_success "PM2 安装完成"
}

# 安装Nginx
install_nginx() {
    log_info "安装Nginx..."
    
    sudo apt install -y nginx
    
    # 启动并启用Nginx
    sudo systemctl start nginx
    sudo systemctl enable nginx
    
    log_success "Nginx安装完成"
}

# 安装SSL证书工具
install_certbot() {
    log_info "安装Certbot..."
    
    sudo apt install -y certbot python3-certbot-nginx
    
    log_success "Certbot安装完成"
}

# 创建应用用户
create_app_user() {
    log_info "创建应用用户..."
    
    # 创建august-lab用户
    if ! id "august-lab" &>/dev/null; then
        sudo useradd -r -s /bin/bash -d /var/lib/august-lab august-lab
        log_success "用户august-lab创建完成"
    else
        log_info "用户august-lab已存在"
    fi
    
    # 创建必要目录
    sudo mkdir -p /var/lib/august-lab/{uploads,products,backups}
    sudo mkdir -p /var/log/august-lab
    sudo mkdir -p /etc/august-lab
    
    # 设置权限
    sudo chown -R august-lab:august-lab /var/lib/august-lab
    sudo chown -R august-lab:august-lab /var/log/august-lab
    
    log_success "应用目录创建完成"
}

# 配置防火墙
setup_firewall() {
    log_info "配置防火墙..."
    
    # 安装ufw
    sudo apt install -y ufw
    
    # 配置防火墙规则
    sudo ufw default deny incoming
    sudo ufw default allow outgoing
    sudo ufw allow ssh
    sudo ufw allow 'Nginx Full'
    
    # 启用防火墙
    sudo ufw --force enable
    
    log_success "防火墙配置完成"
}

# 生成配置文件
generate_config() {
    log_info "生成配置文件..."
    
    # 生成SECRET_KEY
    SECRET_KEY=$(openssl rand -base64 64)
    
    # 创建环境配置文件
    sudo tee /etc/august-lab/.env > /dev/null << EOF
# August.Lab 生产环境配置

# 安全配置
SECRET_KEY=$SECRET_KEY
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 数据库配置 (使用SQLite，无需额外配置)
DATABASE_URL=sqlite:///./august_lab.db

# 文件存储配置
UPLOAD_DIR=/var/lib/august-lab/uploads
PRODUCTS_DIR=/var/lib/august-lab/products
MAX_FILE_SIZE=104857600

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=/var/log/august-lab/app.log

# 域名配置 (需要手动修改)
DOMAIN=your-domain.com
FRONTEND_URL=https://your-domain.com
API_URL=https://your-domain.com/api

# 邮件配置 (可选，需要手动配置)
# SMTP_HOST=smtp.gmail.com
# SMTP_PORT=587
# SMTP_USERNAME=your-email@gmail.com
# SMTP_PASSWORD=your-app-password

# 监控配置 (可选)
# SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
EOF
    
    # 设置配置文件权限
    sudo chown august-lab:august-lab /etc/august-lab/.env
    sudo chmod 600 /etc/august-lab/.env
    
    log_success "配置文件生成完成"
}

# 创建systemd服务
create_systemd_service() {
    log_info "创建systemd服务..."
    
    sudo tee /etc/systemd/system/august-lab.service > /dev/null << 'EOF'
[Unit]
Description=August.Lab API Server
After=network.target

[Service]
Type=simple
User=august-lab
Group=august-lab
WorkingDirectory=/var/www/august-lab/backend
Environment=PATH=/var/www/august-lab/venv/bin
EnvironmentFile=/etc/august-lab/.env
ExecStart=/var/www/august-lab/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=3
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
    
    # 重新加载systemd
    sudo systemctl daemon-reload
    
    log_success "systemd服务创建完成"
}

# 创建Nginx配置
create_nginx_config() {
    log_info "创建Nginx配置..."
    
    sudo tee /etc/nginx/sites-available/august-lab > /dev/null << 'EOF'
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    # 临时配置，SSL配置后会重定向到HTTPS
    root /var/www/august-lab/frontend/dist;
    index index.html;
    
    # 前端静态文件
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # API代理
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        client_max_body_size 100M;
    }
    
    # 产品文件服务
    location /products/ {
        alias /var/lib/august-lab/products/;
        add_header X-Frame-Options "SAMEORIGIN";
        expires 1h;
    }
    
    # 上传文件服务
    location /uploads/ {
        alias /var/lib/august-lab/uploads/;
        expires 1y;
    }
}
EOF
    
    # 启用站点
    sudo ln -sf /etc/nginx/sites-available/august-lab /etc/nginx/sites-enabled/
    
    # 删除默认站点
    sudo rm -f /etc/nginx/sites-enabled/default
    
    # 测试Nginx配置
    sudo nginx -t
    
    log_success "Nginx配置创建完成"
}

# 创建备份脚本
create_backup_scripts() {
    log_info "创建备份脚本..."
    
    # 数据库备份脚本
    sudo tee /usr/local/bin/august-lab-backup-db.sh > /dev/null << 'EOF'
#!/bin/bash
BACKUP_DIR="/var/lib/august-lab/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="august_lab"
DB_USER="august_lab"

mkdir -p $BACKUP_DIR
pg_dump -U $DB_USER -h localhost $DB_NAME | gzip > $BACKUP_DIR/db_backup_$DATE.sql.gz
find $BACKUP_DIR -name "db_backup_*.sql.gz" -mtime +30 -delete

echo "$(date): Database backup completed" >> /var/log/august-lab/backup.log
EOF
    
    # 文件备份脚本
    sudo tee /usr/local/bin/august-lab-backup-files.sh > /dev/null << 'EOF'
#!/bin/bash
BACKUP_DIR="/var/lib/august-lab/backups"
DATE=$(date +%Y%m%d_%H%M%S)
SOURCE_DIRS="/var/lib/august-lab/uploads /var/lib/august-lab/products"

mkdir -p $BACKUP_DIR
tar -czf $BACKUP_DIR/files_backup_$DATE.tar.gz $SOURCE_DIRS 2>/dev/null
find $BACKUP_DIR -name "files_backup_*.tar.gz" -mtime +7 -delete

echo "$(date): Files backup completed" >> /var/log/august-lab/backup.log
EOF
    
    # 设置执行权限
    sudo chmod +x /usr/local/bin/august-lab-backup-db.sh
    sudo chmod +x /usr/local/bin/august-lab-backup-files.sh
    
    log_success "备份脚本创建完成"
}

# 创建监控脚本
create_monitoring_scripts() {
    log_info "创建监控脚本..."
    
    sudo tee /usr/local/bin/august-lab-monitor.sh > /dev/null << 'EOF'
#!/bin/bash
LOG_FILE="/var/log/august-lab/monitor.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

# 检查服务状态
if ! systemctl is-active --quiet august-lab; then
    echo "$DATE - ERROR: August.Lab service is not running" >> $LOG_FILE
    systemctl restart august-lab
fi

if ! systemctl is-active --quiet nginx; then
    echo "$DATE - ERROR: Nginx service is not running" >> $LOG_FILE
    systemctl restart nginx
fi

# 检查磁盘空间
DISK_USAGE=$(df -h / | awk 'NR==2{print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "$DATE - WARNING: Disk usage is ${DISK_USAGE}%" >> $LOG_FILE
fi

# 检查内存使用
MEM_USAGE=$(free | grep Mem | awk '{printf("%.0f", $3/$2 * 100.0)}')
if [ $MEM_USAGE -gt 80 ]; then
    echo "$DATE - WARNING: Memory usage is ${MEM_USAGE}%" >> $LOG_FILE
fi
EOF
    
    sudo chmod +x /usr/local/bin/august-lab-monitor.sh
    
    log_success "监控脚本创建完成"
}

# 设置定时任务
setup_cron_jobs() {
    log_info "设置定时任务..."
    
    # 为august-lab用户创建crontab
    sudo -u august-lab crontab << 'EOF'
# August.Lab 定时任务

# 每天凌晨2点备份数据库
0 2 * * * /usr/local/bin/august-lab-backup-db.sh

# 每天凌晨3点备份文件
0 3 * * * /usr/local/bin/august-lab-backup-files.sh

# 每5分钟检查系统状态
*/5 * * * * /usr/local/bin/august-lab-monitor.sh
EOF
    
    log_success "定时任务设置完成"
}

# 创建部署脚本
create_deploy_script() {
    log_info "创建部署脚本..."
    
    sudo tee /usr/local/bin/august-lab-deploy.sh > /dev/null << 'EOF'
#!/bin/bash

set -e

APP_DIR="/var/www/august-lab"
BACKUP_DIR="/var/lib/august-lab/backups/deploy"
SERVICE_NAME="august-lab"

echo "Starting August.Lab deployment..."

# 检查是否存在应用目录
if [ ! -d "$APP_DIR" ]; then
    echo "Error: Application directory $APP_DIR does not exist"
    echo "Please clone the repository first:"
    echo "sudo git clone https://github.com/your-username/august-lab.git $APP_DIR"
    exit 1
fi

# 创建部署备份
echo "Creating deployment backup..."
mkdir -p $BACKUP_DIR
if [ -d "$APP_DIR" ]; then
    cp -r $APP_DIR $BACKUP_DIR/$(date +%Y%m%d_%H%M%S)
fi

# 切换到应用目录
cd $APP_DIR

# 拉取最新代码
echo "Pulling latest code..."
sudo -u august-lab git pull origin main

# 安装后端依赖
echo "Installing backend dependencies..."
cd backend
if [ ! -d "../venv" ]; then
    python3 -m venv ../venv
fi
source ../venv/bin/activate
pip install -r requirements.txt

# 运行数据库迁移
echo "Running database migrations..."
python manage_db.py

# 构建前端
echo "Building frontend..."
cd ../frontend
npm install
npm run build

# 设置权限
echo "Setting permissions..."
sudo chown -R august-lab:august-lab $APP_DIR
sudo chmod -R 755 $APP_DIR

# 重启服务
echo "Restarting services..."
sudo systemctl restart $SERVICE_NAME
sudo systemctl reload nginx

# 健康检查
echo "Performing health check..."
sleep 5
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "Deployment successful!"
else
    echo "Health check failed! Please check the logs."
    sudo journalctl -u $SERVICE_NAME --no-pager -n 20
    exit 1
fi

echo "Deployment completed successfully!"
EOF
    
    sudo chmod +x /usr/local/bin/august-lab-deploy.sh
    
    log_success "部署脚本创建完成"
}

# 显示安装总结
show_summary() {
    log_success "August.Lab 生产环境安装完成！"
    echo
    echo "=== 安装总结 ==="
    echo "✅ 系统依赖已安装"
    echo "✅ Python 3.8+ 已安装"
    echo "✅ Node.js 18+ 已安装"
    echo "✅ Nginx 已安装并配置"
    echo "✅ 防火墙已配置"
    echo "✅ 系统服务已创建"
    echo "✅ 备份和监控脚本已创建"
    echo "✅ 定时任务已设置"
    echo
    echo "=== 下一步操作 ==="
    echo "1. 克隆应用代码:"
    echo "   sudo git clone https://github.com/your-username/august-lab.git /var/www/august-lab"
    echo
    echo "2. 修改域名配置:"
    echo "   sudo nano /etc/august-lab/.env"
    echo "   sudo nano /etc/nginx/sites-available/august-lab"
    echo
    echo "3. 运行部署脚本:"
    echo "   sudo /usr/local/bin/august-lab-deploy.sh"
    echo
    echo "4. 配置SSL证书:"
    echo "   sudo certbot --nginx -d your-domain.com -d www.your-domain.com"
    echo
    echo "5. 启动服务:"
    echo "   sudo systemctl enable august-lab"
    echo "   sudo systemctl start august-lab"
    echo
    echo "=== 重要文件位置 ==="
    echo "配置文件: /etc/august-lab/.env"
    echo "日志文件: /var/log/august-lab/"
    echo "数据目录: /var/lib/august-lab/"
    echo "备份目录: /var/lib/august-lab/backups/"
    echo "Nginx配置: /etc/nginx/sites-available/august-lab"
    echo
    echo "=== 有用的命令 ==="
    echo "查看服务状态: sudo systemctl status august-lab"
    echo "查看日志: sudo journalctl -u august-lab -f"
    echo "重启服务: sudo systemctl restart august-lab"
    echo "运行备份: sudo /usr/local/bin/august-lab-backup-db.sh"
    echo "部署更新: sudo /usr/local/bin/august-lab-deploy.sh"
    echo
    log_warning "请记得修改 /etc/august-lab/.env 中的域名和其他配置！"
}

# 主函数
main() {
    echo "=== August.Lab 生产环境安装脚本 ==="
    echo
    
    check_root
    check_system
    
    log_info "开始安装过程..."
    
    update_system
    install_dependencies
    install_python
    install_nodejs
    install_nginx
    install_certbot
    
    create_app_user
    setup_firewall
    generate_config
    
    create_systemd_service
    create_nginx_config
    create_backup_scripts
    create_monitoring_scripts
    setup_cron_jobs
    create_deploy_script
    
    show_summary
}

# 运行主函数
main "$@"