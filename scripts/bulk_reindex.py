import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.ingestion.indexer import add_document_to_index

RAW_DOCS_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw_documents")


def get_department(filename):
    if filename.startswith("hr_"):
        return "HR"
    if filename.startswith("it_"):
        return "IT"
    if filename.startswith("company_"):
        return "Company"
    return "Company"  # default fallback


def main():
    files = sorted(os.listdir(RAW_DOCS_DIR))
    supported = [f for f in files if f.lower().endswith((".pdf", ".docx", ".txt", ".md"))]

    print(f"Found {len(supported)} documents to index.\n")

    for i, filename in enumerate(supported, 1):
        file_path = os.path.join(RAW_DOCS_DIR, filename)
        department = get_department(filename)
        try:
            chunk_count, dept = add_document_to_index(file_path, department_override=department)
            print(f"[{i}/{len(supported)}] OK  {filename}  -> {dept}  ({chunk_count} chunks)")
        except Exception as e:
            print(f"[{i}/{len(supported)}] FAILED  {filename}  -> {e}")

    print("\nDone.")


if __name__ == "__main__":
    main()