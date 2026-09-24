FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_SYSTEM_PYTHON=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv==0.4.18

# Install build deps for psycopg/spacy then dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
# Lock file is regenerated on first build if missing
RUN uv sync --no-dev --frozen || uv sync --no-dev

# Download spaCy English model used by Presidio
RUN uv run python -m spacy download en_core_web_sm

COPY app ./app
COPY migrations ./migrations
COPY alembic.ini ./
COPY main.py ./

EXPOSE 8000

# Run migrations then start API
CMD ["sh", "-c", "uv run alembic upgrade head && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000"]
