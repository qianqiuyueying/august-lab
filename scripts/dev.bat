@echo off
REM Windows 开发环境启动脚本

echo 启动 August.Lab 开发环境...

REM 检查依赖
echo 检查依赖...

where node >nul 2>nul
if %errorlevel% neq 0 (
    echo 错误: 未找到 Node.js，请先安装 Node.js
    pause
    exit /b 1
)

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo 错误: 未找到 Python，请先安装 Python
    pause
    exit /b 1
)

echo 依赖检查完成

REM 如果传入 --install 参数，则安装依赖
if "%1"=="--install" (
    echo 安装前端依赖...
    cd frontend
    call npm install
    cd ..
    
    echo 安装后端依赖...
    cd backend
    call pip install -r requirements.txt
    cd ..
)

REM 启动后端服务
echo 启动后端服务...
cd backend
start "Backend Server" cmd /k "uvicorn main:app --reload --host 0.0.0.0 --port 8001"
cd ..

REM 等待后端启动
timeout /t 3 /nobreak >nul

REM 启动前端服务
echo 启动前端服务...
cd frontend
start "Frontend Server" cmd /k "npm run dev"
cd ..

echo.
echo 开发环境已启动！
echo 前端地址: http://localhost:3000
echo 后端地址: http://localhost:8001
echo API文档: http://localhost:8001/docs
echo.
echo 按任意键退出...
pause >nul