FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV REDIS_HOST=redis
ENV REDIS_PORT=6379
ENV KAFKA_BROKER=kafka:9092
ENV KAFKA_TOPIC=travel-data-raw
ENV AMADEUS_CLIENT_ID=3U0F7vgHIN9Xvq31WiQnVVPB6ohfYpT9
ENV AMADEUS_CLIENT_SECRET=g83BzbXv4GzafOCT
# Qdrant defaults (overridable via compose)
ENV QDRANT_URL=http://qdrant:6333
ENV QDRANT_COLLECTION=travel_data
ENV QDRANT_VECTOR_DIM=384
ENV QDRANT_DISTANCE=Cosine

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import redis; redis.Redis(host='redis', port=6379).ping()"

# Run the application
CMD ["python", "testamad.py"]
