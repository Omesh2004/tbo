import os
from qdrant_client import QdrantClient

# Build client from env to avoid hardcoding secrets
QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

qdrant_client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

if __name__ == "__main__":
    # Simple connectivity check
    print(qdrant_client.get_collections())