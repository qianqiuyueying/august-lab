#!/bin/bash

# 开发环境启动脚本

echo "启动 August.Lab 开发环境..."

# 检查是否安装了必要的依赖
check_dependencies() {
    echo "检查依赖..."
    
    # 检查 Node.js
    if ! command -v node &> /dev/null; then
        echo "错误: 未找到 Node.js，请先安装 Node.js"
        exit 1
    fi
    
    # 检查 Python
    if ! command -v python3 &> /dev/null; then
        echo "错误: 未找到 Python3，请先安装 Python3"
        exit 1
    fi
    
    echo "依赖检查完成"
}

# 安装前端依赖
install_frontend_deps() {
    echo "安装前端依赖..."
    cd frontend
    npm install
    cd ..
}

# 安装后端依赖
install_backend_deps() {
    echo "安装后端依赖..."
    cd backend
    pip install -r requirements.txt
    cd ..
}

# 启动后端服务
start_backend() {
    echo "启动后端服务..."
    cd backend
    uvicorn main:app --reload --host 0.0.0.0 --port 8001 &
    BACKEND_PID=$!
    cd ..
    echo "后端服务已启动 (PID: $BACKEND_PID)"
}

# 启动前端服务
start_frontend() {
    echo "启动前端服务..."
    cd frontend
    npm run dev &
    FRONTEND_PID=$!
    cd ..
    echo "前端服务已启动 (PID: $FRONTEND_PID)"
}

# 清理函数
cleanup() {
    echo "正在停止服务..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
    fi
    echo "服务已停止"
    exit 0
}

# 设置信号处理
trap cleanup SIGINT SIGTERM

# 主流程
main() {
    check_dependencies
    
    # 如果传入 --install 参数，则安装依赖
    if [ "$1" = "--install" ]; then
        install_frontend_deps
        install_backend_deps
    fi
    
    start_backend
    sleep 2  # 等待后端启动
    start_frontend
    
    echo ""
    echo "开发环境已启动！"
    echo "前端地址: http://localhost:3000"
    echo "后端地址: http://localhost:8001"
    echo "API文档: http://localhost:8001/docs"
    echo ""
    echo "按 Ctrl+C 停止服务"
    
    # 等待用户中断
    wait
}

main "$@"