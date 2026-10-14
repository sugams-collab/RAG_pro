# ==========================================================
# Production Dockerfile
# ==========================================================

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# ----------------------------------------------------------
# System Dependencies
# ----------------------------------------------------------

RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ----------------------------------------------------------
# Install Python Dependencies
# ----------------------------------------------------------

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt

# ----------------------------------------------------------
# Copy Project
# ----------------------------------------------------------

COPY . .

# ----------------------------------------------------------
# Create Data Directories
# ----------------------------------------------------------

RUN mkdir -p \
    data/raw \
    data/chroma \
    data/bm25 \
    logs

# ----------------------------------------------------------
# API Port
# ----------------------------------------------------------

EXPOSE 8000

# ----------------------------------------------------------
# Health Check
# ----------------------------------------------------------

HEALTHCHECK --interval=30s \
    --timeout=10s \
    --start-period=30s \
    --retries=3 \
CMD curl -f http://localhost:8000/health || exit 1

# ----------------------------------------------------------
# Start API
# ----------------------------------------------------------

CMD [
    "uvicorn",
    "src.api.app:app",
    "--host",
    "0.0.0.0",
    "--port",
    "8000"
]