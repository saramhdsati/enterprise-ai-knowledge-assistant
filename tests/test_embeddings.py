from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim

print("Loading embedding model (first time may take a minute)...")
model = SentenceTransformer("BAAI/bge-small-en-v1.5")
print("[OK] Model loaded successfully\n")

# Two sentences that are similar in MEANING but different in WORDING
sentence_1 = "How many vacation days do I get per year?"
sentence_2 = "Eligible employees can take up to 15 vacation days per year."

# A sentence that is unrelated
sentence_3 = "The VPN client must be used to access internal systems remotely."

# Convert all sentences to embeddings (vectors)
embeddings = model.encode([sentence_1, sentence_2, sentence_3])

print(f"Embedding shape: {embeddings[0].shape}")  # how many numbers per vector
print(f"First 5 numbers of sentence_1's vector: {embeddings[0][:5]}\n")

# Measure similarity between sentences (0 = unrelated, 1 = identical meaning)
similarity_related = cos_sim(embeddings[0], embeddings[1])
similarity_unrelated = cos_sim(embeddings[0], embeddings[2])

print(f"Similarity (vacation question <-> vacation policy): {similarity_related.item():.4f}")
print(f"Similarity (vacation question <-> VPN policy):       {similarity_unrelated.item():.4f}")