import os
from pypdf import PdfReader
from docx import Document


def parse_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text


def parse_docx(file_path):
    doc = Document(file_path)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text


def parse_txt_or_md(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def parse_document(file_path):
    extension = os.path.splitext(file_path)[1].lower()
    if extension == ".pdf":
        return parse_pdf(file_path)
    elif extension == ".docx":
        return parse_docx(file_path)
    elif extension in [".txt", ".md"]:
        return parse_txt_or_md(file_path)
    else:
        raise ValueError(f"Unsupported file type: {extension}")