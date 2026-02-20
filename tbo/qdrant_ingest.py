import os
import hashlib
from typing import Iterable, List, Dict, Any, Optional, Tuple

from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    Distance,
    VectorParams,
    PointStruct,
)


def get_qdrant_client() -> QdrantClient:
    """
    Build a Qdrant client from environment variables.
    - QDRANT_URL (e.g., http://qdrant:6333 or your SaaS endpoint)
    - QDRANT_API_KEY (optional for local, required for SaaS)
    - QDRANT_TIMEOUT (seconds, optional)
    - QDRANT_GRPC ("true" to use gRPC if available)
    """
    url = os.getenv("QDRANT_URL", "http://qdrant:6333")
    api_key = os.getenv("QDRANT_API_KEY")
    timeout = float(os.getenv("QDRANT_TIMEOUT", "30"))
    prefer_grpc = os.getenv("QDRANT_GRPC", "false").lower() == "true"

    client = QdrantClient(url=url, api_key=api_key, timeout=timeout, prefer_grpc=prefer_grpc)
    return client


def ensure_collection(
    client: QdrantClient,
    collection: str,
    vector_size: int,
    distance: str = "Cosine",
) -> None:
    """
    Create the collection if it doesn't exist.
    distance: Cosine | Euclid | Dot
    """
    distances = {
        "cosine": Distance.COSINE,
        "euclid": Distance.EUCLID,
        "dot": Distance.DOT,
    }
    dist = distances.get(distance.lower(), Distance.COSINE)

    existing = client.get_collections()
    names = {c.name for c in existing.collections}
    if collection in names:
        return

    client.create_collection(
        collection_name=collection,
        vectors_config=VectorParams(size=vector_size, distance=dist),
    )


def _hashing_embed(text: str, dim: int) -> List[float]:
    """Deterministic lightweight embedding placeholder based on hashing."""
    vec = [0.0] * dim
    if not text:
        return vec
    # split to pseudo-tokens
    parts = text.lower().split()
    for p in parts:
        h = int(hashlib.sha256(p.encode("utf-8")).hexdigest(), 16)
        # simple feature hashing into dim buckets
        idx = h % dim
        sign = -1.0 if (h >> 1) & 1 else 1.0
        vec[idx] += sign
    # L2 normalize
    norm = sum(v * v for v in vec) ** 0.5 or 1.0
    return [v / norm for v in vec]


def embed_texts(texts: List[str], dim: int) -> List[List[float]]:
    return [_hashing_embed(t, dim) for t in texts]


def prepare_points(
    records: Iterable[Dict[str, Any]],
    vector_dim: int,
    id_key: str = "id",
    text_key: Optional[str] = "text",
    vector_key: Optional[str] = "vector",
    payload_keys: Optional[List[str]] = None,
) -> Tuple[List[PointStruct], int, int]:
    """
    Convert iterable of dict records into Qdrant PointStruct list.
    If vector is missing, compute from text_key using hashing embed.
    payload includes all keys except vector/id by default or restricted to payload_keys.
    Returns: (points, num_embedded, num_with_vectors)
    """
    pts: List[PointStruct] = []
    to_embed_texts: List[str] = []
    embed_indices: List[int] = []
    num_with_vectors = 0

    # First pass – collect and mark embedding needs
    tmp_store: List[Dict[str, Any]] = []
    for rec in records:
        rid = rec.get(id_key)
        if rid is None:
            continue
        vec = rec.get(vector_key) if vector_key else None
        if isinstance(vec, list) and len(vec) == vector_dim:
            num_with_vectors += 1
            tmp_store.append({"id": rid, "vector": vec, "raw": rec})
        else:
            text = rec.get(text_key, "") if text_key else ""
            to_embed_texts.append(str(text))
            embed_indices.append(len(tmp_store))
            tmp_store.append({"id": rid, "vector": None, "text": text, "raw": rec})

    # Embed if needed
    num_embedded = 0
    if to_embed_texts:
        embedded = embed_texts(to_embed_texts, vector_dim)
        for i, vec in zip(embed_indices, embedded):
            tmp_store[i]["vector"] = vec
            num_embedded += 1

    # Build payloads and PointStructs
    for item in tmp_store:
        raw = item["raw"]
        if payload_keys is None:
            payload = {k: v for k, v in raw.items() if k not in {id_key, vector_key}}
        else:
            payload = {k: raw.get(k) for k in payload_keys}
        pts.append(PointStruct(id=item["id"], vector=item["vector"], payload=payload))

    return pts, num_embedded, num_with_vectors


def upsert_records(
    collection: str,
    records: Iterable[Dict[str, Any]],
    vector_dim: int,
    distance: str = "Cosine",
    batch_size: int = 256,
) -> Dict[str, Any]:
    """
    High-level helper to upsert a stream of records to Qdrant.
    Each record should contain at minimum an 'id' and either a 'vector' of length vector_dim
    or a 'text' field to embed.
    """
    client = get_qdrant_client()
    ensure_collection(client, collection, vector_dim, distance)

    buffer: List[PointStruct] = []
    total = 0
    embedded = 0
    with_vec = 0

    def flush():
        nonlocal buffer, total
        if not buffer:
            return
        client.upsert(collection_name=collection, points=buffer)
        total += len(buffer)
        buffer = []

    pts, e_cnt, v_cnt = prepare_points(records, vector_dim)
    embedded += e_cnt
    with_vec += v_cnt

    for p in pts:
        buffer.append(p)
        if len(buffer) >= batch_size:
            flush()
    flush()

    return {
        "upserted": total,
        "embedded": embedded,
        "with_vectors": with_vec,
        "collection": collection,
        "vector_dim": vector_dim,
    }
