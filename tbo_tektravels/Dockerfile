FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY tbo_hotel_client.py .
COPY tektravels_flight_client.py .
COPY testamad_tbo.py .
COPY qdrant_ingest.py .
COPY connect.py .

# Set environment variables with defaults
ENV REDIS_HOST=tbo-redis \
    REDIS_PORT=6379 \
    KAFKA_BROKER=tbo-kafka:9092 \
    KAFKA_TOPIC=travel-data-raw-tbo \
    QDRANT_URL=http://tbo-qdrant:6333 \
    QDRANT_COLLECTION=travel_data \
    QDRANT_VECTOR_DIM=384 \
    QDRANT_DISTANCE=Cosine \
    TBO_HOTEL_USERNAME=Hackathon \
    TBO_HOTEL_PASSWORD=Hackathon@1234 \
    TEKTRAVELS_FLIGHT_USER_ID=Hackathon \
    TEKTRAVELS_FLIGHT_PASSWORD=Hackathon@123

# Health check - verify Redis connectivity every 30 seconds
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import redis; redis.Redis(host='tbo-redis', port=6379).ping()" || exit 1

# Run the main application
CMD ["python", "testamad_tbo.py"]
