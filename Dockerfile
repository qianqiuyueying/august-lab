FROM python:3.14-slim AS builder

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY backend/requirements.txt .
RUN uv pip install --system --no-cache-dir -r requirements.txt

COPY backend/app/ ./app/
COPY backend/alembic/ ./alembic/
COPY backend/alembic.ini .

FROM python:3.14-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY --from=builder /usr/local/lib/python3.14/site-packages/ /usr/local/lib/python3.14/site-packages/
COPY --from=builder /app/ .

RUN mkdir -p /app/data

ENV PYTHONUNBUFFERED=1
ENV BLOG_DATABASE_URL=sqlite+aiosqlite:///./data/blog.db

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
