import PyPDF2
from docx import Document


def extract_text(filepath):
    """Extract text from PDF or DOCX files."""
    if filepath.lower().endswith('.pdf'):
        return extract_pdf_text(filepath)
    elif filepath.lower().endswith('.docx'):
        return extract_docx_text(filepath)
    else:
        raise ValueError("Unsupported file format. Only PDF and DOCX are supported.")


def extract_pdf_text(filepath):
    text = ""
    with open(filepath, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


def extract_docx_text(filepath):
    doc = Document(filepath)
    paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
    return '\n'.join(paragraphs)
