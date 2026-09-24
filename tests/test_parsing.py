import os
from pypdf import PdfReader
from docx import Document


def parse_pdf(file_path):
    """Extract text from a PDF file"""
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text


def parse_docx(file_path):
    """Extract text from a DOCX file"""
    doc = Document(file_path)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text


def parse_txt_or_md(file_path):
    """Extract text from a TXT or MD file"""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def parse_document(file_path):
    """
    Universal parser: detects file type from its extension
    and calls the right function automatically.
    """
    extension = os.path.splitext(file_path)[1].lower()

    if extension == ".pdf":
        return parse_pdf(file_path)
    elif extension == ".docx":
        return parse_docx(file_path)
    elif extension in [".txt", ".md"]:
        return parse_txt_or_md(file_path)
    else:
        raise ValueError(f"Unsupported file type: {extension}")

import re

def clean_text(text):
    """
    Cleans raw extracted text:
    - Removes table-of-contents dot leaders (e.g. "....2")
    - Collapses multiple blank lines into one
    - Collapses multiple spaces into one
    - Strips leading/trailing whitespace per line
    """
    # 1) Remove sequences of 4+ dots (with optional spaces between them)
    text = re.sub(r'\.{4,}\s*\d*', '', text)

    # 2) Collapse 3+ consecutive newlines into just 2 (one blank line)
    text = re.sub(r'\n{3,}', '\n\n', text)

    # 3) Collapse multiple spaces/tabs into a single space
    text = re.sub(r'[ \t]{2,}', ' ', text)

    # 4) Strip trailing whitespace from each line
    lines = [line.rstrip() for line in text.split('\n')]
    text = '\n'.join(lines)

    # 5) Strip leading/trailing whitespace from the whole text
    return text.strip()

# --- Run on ALL files in data/raw_documents ---

folder = "data/raw_documents"

for filename in os.listdir(folder):
    file_path = os.path.join(folder, filename)
    try:
        raw_text = parse_document(file_path)
        cleaned_text = clean_text(raw_text)
        print(f"[OK] {filename} -> raw: {len(raw_text)} chars | cleaned: {len(cleaned_text)} chars")
    except Exception as e:
        print(f"[FAILED] {filename} -> {e}")

# --- Show a before/after example on the PDF (the one with dot leaders) ---
print("\n" + "="*60)
print("BEFORE/AFTER example (hr_employee_handbook.pdf):")
print("="*60)

raw = parse_document("data/raw_documents/hr_employee_handbook.pdf")
cleaned = clean_text(raw)

print("\n--- BEFORE (chars 200-500) ---")
print(raw[200:500])

print("\n--- AFTER (chars 200-500) ---")
print(cleaned[200:500])

# chunk 

def chunk_by_headings(text, min_chunk_size=100):
    """
    Splits text into chunks based on heading patterns.
    Recognizes headings like:
    - "## Something" (Markdown)
    - "1. Something" or "1.5 - Something" (numbered sections)
    Falls back to keeping small pieces attached to the previous chunk.
    """
    # Pattern matches lines that look like headings
    heading_pattern = re.compile(
        r'^(#{1,3}\s+.+|(\d+\.)+\d*\s*[-–]?\s*.+)$',
        re.MULTILINE
    )

    lines = text.split('\n')
    chunks = []
    current_chunk = []

    for line in lines:
        is_heading = bool(heading_pattern.match(line.strip())) and len(line.strip()) < 100

        if is_heading and current_chunk:
            # Save the previous chunk before starting a new one
            chunk_text = '\n'.join(current_chunk).strip()
            if chunk_text:
                chunks.append(chunk_text)
            current_chunk = [line]
        else:
            current_chunk.append(line)

    # Don't forget the last chunk
    if current_chunk:
        chunk_text = '\n'.join(current_chunk).strip()
        if chunk_text:
            chunks.append(chunk_text)

    # Merge chunks that are too small into the next one (avoid tiny fragments)
    merged_chunks = []
    buffer = ""
    for chunk in chunks:
        buffer = (buffer + "\n\n" + chunk).strip() if buffer else chunk
        if len(buffer) >= min_chunk_size:
            merged_chunks.append(buffer)
            buffer = ""
    if buffer:
        if merged_chunks:
            merged_chunks[-1] += "\n\n" + buffer
        else:
            merged_chunks.append(buffer)

    return merged_chunks


# --- Test chunking on one file ---
print("\n" + "="*60)
print("CHUNKING TEST (hr_leave_policy.md):")
print("="*60)

raw = parse_document("data/raw_documents/hr_leave_policy.md")
cleaned = clean_text(raw)
chunks = chunk_by_headings(cleaned)

print(f"\nTotal chunks created: {len(chunks)}\n")

for i, chunk in enumerate(chunks):
    print(f"--- Chunk {i+1} ({len(chunk)} chars) ---")
    print(chunk[:150])
    print()