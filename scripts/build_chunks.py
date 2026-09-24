import os
import json
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.ingestion.parsing import parse_document
from app.ingestion.cleaning import clean_text
from app.ingestion.chunking import chunk_by_headings
from app.ingestion.metadata import get_department


def build_all_chunks(input_folder="data/raw_documents"):
    all_chunks = []
    chunk_counter = 0
    filenames = sorted(os.listdir(input_folder))

    for filename in filenames:
        file_path = os.path.join(input_folder, filename)
        try:
            raw_text = parse_document(file_path)
            cleaned_text = clean_text(raw_text)
            chunks = chunk_by_headings(cleaned_text)
            department = get_department(filename)

            for i, chunk_text in enumerate(chunks):
                chunk_counter += 1
                all_chunks.append({
                    "chunk_id": f"chunk_{chunk_counter:04d}",
                    "source_file": filename,
                    "department": department,
                    "chunk_index_in_doc": i + 1,
                    "total_chunks_in_doc": len(chunks),
                    "char_count": len(chunk_text),
                    "text": chunk_text
                })
            print(f"[OK] {filename} ({department}) -> {len(chunks)} chunks")
        except Exception as e:
            print(f"[FAILED] {filename} -> {e}")

    return all_chunks


if __name__ == "__main__":
    chunks = build_all_chunks()
    print(f"\nTOTAL CHUNKS: {len(chunks)}")
    os.makedirs("data/processed", exist_ok=True)
    with open("data/processed/chunks.json", "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)
    print("Saved to data/processed/chunks.json")