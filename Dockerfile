# August.Lab Dockerfile
# 多阶段构建，优化镜像大小

# ==================== 后端构建阶段 ====================
FROM python:3.11-slim AS backend-builder

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY backend/requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir --retries 5 --timeout 120 -r requirements.txt

# ==================== 前端构建阶段 ====================
FROM node:18-alpine AS frontend-builder

WORKDIR /app

# 复制前端依赖文件
COPY frontend/package*.json ./

# 安装前端依赖（需要 devDependencies 以支持构建）
RUN npm ci

# 复制前端源代码
COPY frontend/ .

# 构建前端
RUN npm run build

# ==================== 生产运行阶段 ====================
FROM python:3.11-slim

WORKDIR /app

# 安装运行时依赖
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 创建非root用户
RUN useradd -m -u 1000 august && \
    mkdir -p /app/backend/uploads /app/backend/products /app/logs /app/data && \
    chown -R august:august /app

# 从构建阶段复制Python依赖
COPY --from=backend-builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend-builder /usr/local/bin /usr/local/bin

# 复制后端代码
COPY --chown=august:august backend/ ./backend/

# 复制前端构建产物
COPY --from=frontend-builder --chown=august:august /app/dist ./frontend/dist

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PORT=8000
ENV PYTHONPATH=/app/backend

# 切换到非root用户
USER august

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 启动命令
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
