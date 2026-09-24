import numpy as np
from qdrant_client.models import Filter, FieldCondition, MatchAny
from app.core import state

RERANK_CANDIDATES = 20  # عدد الـ chunks اللي بتاخد من RRF قبل الـ reranking
RERANK_THRESHOLD = -8.0  # أي chunk درجته أقل من كده بيتشال، معتبرينه مش relevant


def hybrid_search(question, top_k=4, allowed_departments=None):
    allow_all = allowed_departments is None or "ALL" in allowed_departments

    question_embedding = state.embedding_model.encode(question).tolist()

    qdrant_filter = None
    if not allow_all:
        qdrant_filter = Filter(
            must=[FieldCondition(key="department", match=MatchAny(any=allowed_departments))]
        )

    qdrant_results = state.qdrant_client.query_points(
        collection_name=state.QDRANT_COLLECTION,
        query=question_embedding,
        query_filter=qdrant_filter,
        limit=len(state.chunks)
    ).points

    semantic_ranking = [point.id for point in qdrant_results]

    if state.bm25 is None:
        bm25_scores = np.zeros(len(state.chunks))
    else:
        bm25_scores = state.bm25.get_scores(question.lower().split())
    bm25_ranking = np.argsort(-bm25_scores)

    k = 60
    rrf_scores = {}

    for rank, idx in enumerate(semantic_ranking):
        rrf_scores[idx] = rrf_scores.get(idx, 0) + 1 / (k + rank + 1)

    for rank, idx in enumerate(bm25_ranking):
        if not allow_all and state.chunks[idx]["department"] not in allowed_departments:
            continue
        rrf_scores[idx] = rrf_scores.get(idx, 0) + 1 / (k + rank + 1)

    final_ranking = sorted(rrf_scores.items(), key=lambda x: -x[1])

    candidate_indices = [idx for idx, score in final_ranking[:RERANK_CANDIDATES]]
    candidate_chunks = [state.chunks[idx] for idx in candidate_indices]

    if not candidate_chunks:
        return []

    pairs = [[question, chunk["text"]] for chunk in candidate_chunks]
    rerank_scores = state.reranker_model.predict(pairs)

    if "insurance plan options" in question.lower():
        print(f"\n--- RERANK DEBUG for: {question} ---")
        for chunk, score in sorted(zip(candidate_chunks, rerank_scores), key=lambda x: -x[1]):
            print(f"score={score:.4f}  [{chunk['source_file']}] {chunk['text'][:80]}")
        print("--- END RERANK DEBUG ---\n")

    reranked = sorted(zip(candidate_chunks, rerank_scores), key=lambda x: -x[1])

    # ---------- فلترة بالـ threshold: نشيل أي chunk درجته واطية جدًا ----------
    top_chunks = [chunk for chunk, score in reranked[:top_k] if score >= RERANK_THRESHOLD]

    return top_chunks