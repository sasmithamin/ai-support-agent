# ── Base Image ──────────────────────────────────────────
FROM python:3.11-slim

LABEL description="AI Customer Support Agent"
LABEL version="1.0.0"

# ── Environment Variables ────────────────────────────────
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# ── System Dependencies ──────────────────────────────────
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    git \
    build-essential \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# ── Working Directory ────────────────────────────────────
WORKDIR /app

# ── Upgrade pip first ────────────────────────────────────
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# ── Install Dependencies in stages ──────────────────────
# Stage 1: Core packages first
RUN pip install --no-cache-dir \
    fastapi>=0.109.0 \
    uvicorn[standard]>=0.27.0 \
    pydantic>=2.5.3 \
    pydantic-settings>=2.1.0 \
    python-dotenv>=1.0.0

# Stage 2: Database packages
RUN pip install --no-cache-dir \
    sqlalchemy>=2.0.25 \
    asyncpg>=0.29.0 \
    psycopg2-binary>=2.9.9 \
    alembic>=1.13.1

# Stage 3: AI packages (heaviest)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Copy Application Code ────────────────────────────────
COPY . .

# ── Create Required Directories ──────────────────────────
RUN mkdir -p \
    data/chroma_db \
    data/knowledge_base \
    logs

# ── Expose Port ──────────────────────────────────────────
EXPOSE 8000

# ── Health Check ─────────────────────────────────────────
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# ── Run Application ──────────────────────────────────────
CMD ["python", "scripts/run_server.py"]