# syntax=docker/dockerfile:1
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1     PYTHONUNBUFFERED=1     PIP_DISABLE_PIP_VERSION_CHECK=1     PIP_NO_CACHE_DIR=1     PORT=8501

# System deps for numpy/matplotlib
RUN apt-get update && apt-get install -y --no-install-recommends \ 
    build-essential \ 
    libatlas-base-dev \ 
    libfreetype6-dev \ 
    libjpeg-dev \ 
    libpng-dev \ 
    fonts-dejavu-core \ 
    curl \ 
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Pre-copy requirements to leverage layer caching
COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

# Copy app
COPY . /app

EXPOSE 8501

# Healthcheck (best-effort)
HEALTHCHECK --interval=30s --timeout=5s --retries=10 CMD curl -f http://localhost:${PORT:-8501}/_stcore/health || exit 1

# Allow overriding PORT at runtime; streamlit binds to 0.0.0.0
CMD ["bash", "-lc", "streamlit run Capstone.py --server.port ${PORT:-8501} --server.address 0.0.0.0"]
