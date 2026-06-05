FROM python:3.12-slim AS builder
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app
COPY worker/requirements.txt /app/requirements.txt
RUN apt-get update && apt-get install -y build-essential gcc libpq-dev --no-install-recommends \
    && pip wheel --no-cache-dir --wheel-dir /wheels -r /app/requirements.txt \
    && apt-get purge -y build-essential gcc libpq-dev \
    && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*

FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
RUN useradd -m appuser
WORKDIR /app
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/*
COPY backend /app/backend
COPY worker /app/worker
USER appuser
CMD ["python", "-m", "worker.main"]
