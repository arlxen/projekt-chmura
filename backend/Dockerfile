FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY backend/requirements.txt /app/requirements.txt
RUN apt-get update && apt-get install -y build-essential gcc libpq-dev --no-install-recommends \
    && pip wheel --no-cache-dir --wheel-dir /wheels -r /app/requirements.txt \
    && apt-get purge -y build-essential gcc libpq-dev \
    && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*

FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN useradd -m appuser
WORKDIR /app

# install wheels from builder
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/* || true

COPY backend /app/backend

USER appuser
EXPOSE 8000
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
