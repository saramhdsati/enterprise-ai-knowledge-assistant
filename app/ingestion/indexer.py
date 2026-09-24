import os
from qdrant_client.models import PointStruct
from app.core import state
from app.ingestion.parsing import parse_document
from app.ingestion.cleaning import clean_text
from app.ingestion.chunking import chunk_by_headings
from app.ingestion.metadata import get_department


def add_document_to_index(file_path, department_override=None):
    filename = os.path.basename(file_path)
    raw_text = parse_document(file_path)
    cleaned_text = clean_text(raw_text)
    new_chunks_text = chunk_by_headings(cleaned_text)
    department = department_override or get_department(filename)

    start_id = len(state.chunks)
    new_chunk_dicts = []
    for i, text in enumerate(new_chunks_text):
        embedding = state.embedding_model.encode(text).tolist()
        new_chunk_dicts.append({
            "chunk_id": f"chunk_{start_id + i + 1:04d}",
            "source_file": filename,
            "department": department,
            "chunk_index_in_doc": i + 1,
            "total_chunks_in_doc": len(new_chunks_text),
            "char_count": len(text),
            "text": text,
            "embedding": embedding
        })

    state.chunks.extend(new_chunk_dicts)

    points = [
        PointStruct(
            id=start_id + i,
            vector=c["embedding"],
            payload={
                "chunk_id": c["chunk_id"],
                "source_file": c["source_file"],
                "department": c["department"],
                "text": c["text"],
                "char_count": c["char_count"]
            }
        )
        for i, c in enumerate(new_chunk_dicts)
    ]
    state.qdrant_client.upsert(collection_name=state.QDRANT_COLLECTION, points=points)

    state.rebuild_bm25()
    state.save_chunks()

    return len(new_chunk_dicts), department


def list_all_documents():
    docs = {}
    for c in state.chunks:
        key = c["source_file"]
        if key not in docs:
            docs[key] = {"filename": key, "department": c["department"], "chunk_count": 0}
        docs[key]["chunk_count"] += 1
    return list(docs.values())