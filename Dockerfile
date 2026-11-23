# Lightweight Python 3.11 Debian image
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=10000

# Install system utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install web requirements
COPY web_app/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application assets, datasets, and web app
COPY data/ data/
COPY assets/ assets/
COPY SuvarnaProject_data/ SuvarnaProject_data/
COPY config.json config.json
COPY web_app/ web_app/

EXPOSE 10000

CMD ["sh", "-c", "uvicorn web_app.main:app --host 0.0.0.0 --port ${PORT:-10000}"]
