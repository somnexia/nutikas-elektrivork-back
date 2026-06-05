FROM python:3.13-slim AS builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt



FROM python:3.13-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

# Non root user
RUN useradd -m -u 1000 appuser


COPY --from=builder /app/wheels /images/wheels
COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache /images/wheels/*


COPY . .

RUN chown -R appuser:appuser /app
USER appuser

EXPOSE $PORT

# Запуск через gunicorn с uvicorn-воркерами (стандарт для продакшна на Python)
# Если ваш главный файл лежит в папке src, замените "main:app" на "src.main:app"
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000", "--workers", "1", "app.main:app"]