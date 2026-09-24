import json
import numpy as np
from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim

# 1) Load our chunks (with their embeddings)
with open("data/processed/chunks_with_embeddings.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)

# 2) Load the same embedding model
model = SentenceTransformer("BAAI/bge-small-en-v1.5")

# 3) A real question an employee might ask
question = "How many sick days am I allowed to take?"

# 4) Convert the question to an embedding
question_embedding = model.encode(question)

# 5) Compare the question to EVERY chunk and calculate similarity
chunk_embeddings = np.array([chunk["embedding"] for chunk in chunks], dtype=np.float32)
similarities = cos_sim(question_embedding, chunk_embeddings)[0]

# 6) Find the top 3 most similar chunks
top_indices = np.argsort(-similarities)[:3]  # sort descending, take top 3

print(f"Question: {question}\n")
print("="*60)
print("TOP 3 MOST RELEVANT CHUNKS:")
print("="*60)

for rank, idx in enumerate(top_indices, start=1):
    chunk = chunks[idx]
    score = similarities[idx].item()
    print(f"\n#{rank} | Score: {score:.4f} | Source: {chunk['source_file']}")
    print(f"Text: {chunk['text'][:200]}...")