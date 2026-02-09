#!/bin/bash

# August.Lab 快速部署脚本
# 适用于 Docker 部署方式

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# 检查 Docker
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose 未安装，请先安装 Docker Compose"
        exit 1
    fi
}

# 检查环境变量文件
check_env() {
    if [ ! -f ".env" ]; then
        log_warning ".env 文件不存在，从 env.example 创建"
        if [ -f "env.example" ]; then
            cp env.example .env
            log_warning "请编辑 .env 文件，修改必要的配置（特别是 SECRET_KEY 和管理员密码）"
            log_warning "然后重新运行此脚本"
            exit 1
        else
            log_error "env.example 文件不存在"
            exit 1
        fi
    fi
}

# 生成 SECRET_KEY
generate_secret_key() {
    if grep -q "your-super-secret-key-here" .env; then
        log_info "生成新的 SECRET_KEY..."
        SECRET_KEY=$(openssl rand -base64 64 | tr -d '\n')
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            sed -i '' "s|SECRET_KEY=.*|SECRET_KEY=$SECRET_KEY|" .env
        else
            # Linux
            sed -i "s|SECRET_KEY=.*|SECRET_KEY=$SECRET_KEY|" .env
        fi
        log_success "SECRET_KEY 已生成"
    fi
}

# 构建并启动服务
deploy() {
    log_info "开始部署..."
    
    # 停止现有容器
    log_info "停止现有容器..."
    docker-compose down 2>/dev/null || true
    
    # 构建镜像
    log_info "构建 Docker 镜像..."
    docker-compose build
    
    # 启动服务
    log_info "启动服务..."
    docker-compose up -d
    
    # 等待服务启动
    log_info "等待服务启动..."
    sleep 5
    
    # 健康检查
    log_info "检查服务健康状态..."
    for i in {1..30}; do
        if curl -f http://localhost:8000/health > /dev/null 2>&1; then
            log_success "服务启动成功！"
            return 0
        fi
        sleep 1
    done
    
    log_error "服务健康检查失败"
    log_info "查看日志：docker-compose logs"
    exit 1
}

# 显示部署信息
show_info() {
    log_success "部署完成！"
    echo
    echo "=== 服务信息 ==="
    echo "前端地址: http://localhost"
    echo "API 地址: http://localhost:8000"
    echo "API 文档: http://localhost:8000/docs"
    echo
    echo "=== 常用命令 ==="
    echo "查看日志: docker-compose logs -f"
    echo "停止服务: docker-compose down"
    echo "重启服务: docker-compose restart"
    echo "查看状态: docker-compose ps"
    echo
    log_warning "请确保已配置 Nginx 反向代理和 SSL 证书（生产环境）"
}

# 主函数
main() {
    echo "=== August.Lab 快速部署脚本 ==="
    echo
    
    check_docker
    check_env
    generate_secret_key
    deploy
    show_info
}

main "$@"

