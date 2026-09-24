import json
from rank_bm25 import BM25Okapi

# 1) Load our chunks
with open("data/processed/chunks.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)

# 2) BM25 needs the text split into words (tokenized), not raw strings
tokenized_chunks = [chunk["text"].lower().split() for chunk in chunks]

# 3) Build the BM25 index over all chunks
bm25 = BM25Okapi(tokenized_chunks)

# 4) Same question as before, tokenized the same way
question = "How many sick days am I allowed to take?"
tokenized_question = question.lower().split()

# 5) Get a score for EVERY chunk against this question
scores = bm25.get_scores(tokenized_question)

# 6) Find the top 3 highest-scoring chunks
import numpy as np
top_indices = np.argsort(-scores)[:3]

print(f"Question: {question}\n")
print("="*60)
print("TOP 3 CHUNKS (BM25 keyword search):")
print("="*60)

for rank, idx in enumerate(top_indices, start=1):
    chunk = chunks[idx]
    score = scores[idx]
    print(f"\n#{rank} | Score: {score:.4f} | Source: {chunk['source_file']}")
    print(f"Text: {chunk['text'][:200]}...")