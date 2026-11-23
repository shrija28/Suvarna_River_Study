FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

# Install minimal OS dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install web requirements
COPY web_app/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application assets and datasets
COPY data/ data/
COPY assets/ assets/
COPY SuvarnaProject_data/ SuvarnaProject_data/
COPY config.json config.json
COPY web_app/ web_app/

EXPOSE 8000

CMD ["sh", "-c", "uvicorn web_app.main:app --host 0.0.0.0 --port ${PORT}"]
