import json
import numpy as np
from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim
from rank_bm25 import BM25Okapi

# 1) Load chunks (with embeddings already generated)
with open("data/processed/chunks_with_embeddings.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)

question = "How many sick days am I allowed to take?"

# ============================================================
# SEMANTIC SEARCH (embeddings)
# ============================================================
model = SentenceTransformer("BAAI/bge-small-en-v1.5")
question_embedding = model.encode(question)
chunk_embeddings = np.array([c["embedding"] for c in chunks], dtype=np.float32)
semantic_scores = cos_sim(question_embedding, chunk_embeddings)[0].numpy()

# Rank chunks by semantic score (best first)
semantic_ranking = np.argsort(-semantic_scores)

# ============================================================
# BM25 (keyword search)
# ============================================================
tokenized_chunks = [c["text"].lower().split() for c in chunks]
bm25 = BM25Okapi(tokenized_chunks)
bm25_scores = bm25.get_scores(question.lower().split())

# Rank chunks by BM25 score (best first)
bm25_ranking = np.argsort(-bm25_scores)

# ============================================================
# HYBRID: Reciprocal Rank Fusion (RRF)
# ============================================================
# Idea: a chunk gets a high fused score if it ranks well in EITHER list,
# and an even higher score if it ranks well in BOTH.

k = 60  # standard RRF constant, softens the effect of exact rank position
rrf_scores = {}

for rank, idx in enumerate(semantic_ranking):
    rrf_scores[idx] = rrf_scores.get(idx, 0) + 1 / (k + rank + 1)

for rank, idx in enumerate(bm25_ranking):
    rrf_scores[idx] = rrf_scores.get(idx, 0) + 1 / (k + rank + 1)

# Sort chunks by their combined RRF score
final_ranking = sorted(rrf_scores.items(), key=lambda x: -x[1])

# ============================================================
# Show final top 3 results
# ============================================================
print(f"Question: {question}\n")
print("="*60)
print("TOP 3 CHUNKS (HYBRID: semantic + BM25):")
print("="*60)

for rank, (idx, score) in enumerate(final_ranking[:3], start=1):
    chunk = chunks[idx]
    print(f"\n#{rank} | RRF Score: {score:.4f} | Source: {chunk['source_file']}")
    print(f"Text: {chunk['text'][:200]}...")