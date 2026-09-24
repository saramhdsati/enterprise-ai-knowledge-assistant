import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from qdrant_client.models import VectorParams, Distance
from app.db.qdrant_client import get_qdrant_client, QDRANT_COLLECTION

client = get_qdrant_client()

client.create_collection(
    collection_name=QDRANT_COLLECTION,
    vectors_config=VectorParams(size=384, distance=Distance.COSINE),
)

print(f"Collection '{QDRANT_COLLECTION}' created successfully.")