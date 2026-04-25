FROM python:3.14-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir \
    --index-url https://pypi.tuna.tsinghua.edu.cn/simple \
    --trusted-host pypi.tuna.tsinghua.edu.cn \
    -r requirements.txt

COPY backend/app/ ./app/
COPY backend/alembic/ ./alembic/
COPY backend/alembic.ini .

RUN mkdir -p /app/data /app/products /app/uploads

ENV PYTHONUNBUFFERED=1
ENV BLOG_DATABASE_URL=sqlite+aiosqlite:///./data/blog.db
ENV BLOG_UPLOADS_DIR=/app/uploads
ENV BLOG_PRODUCTS_DIR=/app/products

EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
