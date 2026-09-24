import json
import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi
from groq import Groq
from sentence_transformers import SentenceTransformer, CrossEncoder
from app.db.qdrant_client import get_qdrant_client, QDRANT_COLLECTION

load_dotenv()

CHUNKS_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "data", "processed", "chunks_with_embeddings.json"
)

print("Loading chunks and models...")
with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
    chunks = json.load(f)

embedding_model = SentenceTransformer("BAAI/bge-small-en-v1.5")
print("Loading reranker model...")
reranker_model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
print("[OK] Reranker loaded\n")
qdrant_client = get_qdrant_client()
tokenized_chunks = [c["text"].lower().split() for c in chunks]
bm25 = BM25Okapi(tokenized_chunks) if tokenized_chunks else None
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
print("[OK] Everything loaded\n")


def save_chunks():
    with open(CHUNKS_PATH, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False)


def rebuild_bm25():
    global tokenized_chunks, bm25
    tokenized_chunks = [c["text"].lower().split() for c in chunks]
    bm25 = BM25Okapi(tokenized_chunks) if tokenized_chunks else None