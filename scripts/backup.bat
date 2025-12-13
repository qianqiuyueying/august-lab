@echo off
REM August.Lab Windows 备份脚本

setlocal enabledelayedexpansion

set BACKUP_DIR=backups
set DATE=%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set DATE=!DATE: =0!
set RETENTION_DAYS=30

echo [INFO] === August.Lab 备份开始 ===
echo [INFO] 备份目录: %BACKUP_DIR%
echo [INFO] 保留天数: %RETENTION_DAYS%

REM 创建备份目录
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"

REM 备份SQLite数据库
if exist "august_lab.db" (
    echo [INFO] 开始备份数据库...
    copy "august_lab.db" "%BACKUP_DIR%\db_backup_%DATE%.sqlite" >nul
    echo [INFO] SQLite数据库备份完成
) else (
    echo [WARNING] 未找到数据库文件，跳过数据库备份
)

REM 备份文件
echo [INFO] 开始备份文件...
if exist "backend\uploads" (
    tar -czf "%BACKUP_DIR%\files_backup_%DATE%.tar.gz" backend\uploads backend\products 2>nul
    echo [INFO] 文件备份完成
) else (
    echo [WARNING] 未找到上传目录，跳过文件备份
)

REM 清理旧备份（简单实现，保留最近30天的备份）
echo [INFO] 清理旧备份...
forfiles /p "%BACKUP_DIR%" /m "*_backup_*" /d -%RETENTION_DAYS% /c "cmd /c del @path" 2>nul

echo [INFO] === 备份完成 ===

pause
