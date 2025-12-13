#!/bin/bash

# August.Lab 备份脚本
# 用于备份数据库和文件

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 配置
BACKUP_DIR="${BACKUP_DIR:-./backups}"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS="${RETENTION_DAYS:-30}"

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# 创建备份目录
mkdir -p "$BACKUP_DIR"

# 备份数据库
backup_database() {
    log_info "开始备份数据库..."
    
    # 检查SQLite数据库文件
    if [ -f "august_lab.db" ]; then
        DB_BACKUP_FILE="$BACKUP_DIR/db_backup_$DATE.sqlite"
        cp august_lab.db "$DB_BACKUP_FILE"
        gzip "$DB_BACKUP_FILE"
        log_info "SQLite数据库备份完成: ${DB_BACKUP_FILE}.gz"
    else
        log_warning "未找到数据库文件 august_lab.db，跳过数据库备份"
    fi
}

# 备份文件
backup_files() {
    log_info "开始备份文件..."
    
    FILES_BACKUP_FILE="$BACKUP_DIR/files_backup_$DATE.tar.gz"
    
    # 备份上传文件和产品文件
    tar -czf "$FILES_BACKUP_FILE" \
        backend/uploads \
        backend/products \
        2>/dev/null || log_warning "部分文件备份失败（可能文件不存在）"
    
    if [ -f "$FILES_BACKUP_FILE" ]; then
        log_info "文件备份完成: $FILES_BACKUP_FILE"
    else
        log_warning "文件备份失败"
    fi
}

# 清理旧备份
cleanup_old_backups() {
    log_info "清理 $RETENTION_DAYS 天前的备份..."
    
    find "$BACKUP_DIR" -name "db_backup_*.sqlite.gz" -mtime +$RETENTION_DAYS -delete
    find "$BACKUP_DIR" -name "files_backup_*.tar.gz" -mtime +$RETENTION_DAYS -delete
    
    log_info "旧备份清理完成"
}

# 主函数
main() {
    log_info "=== August.Lab 备份开始 ==="
    log_info "备份目录: $BACKUP_DIR"
    log_info "保留天数: $RETENTION_DAYS"
    
    backup_database
    backup_files
    cleanup_old_backups
    
    log_info "=== 备份完成 ==="
    
    # 显示备份文件大小
    log_info "备份文件列表:"
    ls -lh "$BACKUP_DIR"/*_backup_* 2>/dev/null | tail -5 || log_warning "无备份文件"
}

# 运行主函数
main "$@"
