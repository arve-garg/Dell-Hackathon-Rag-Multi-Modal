import fitz  # PyMuPDF
import docx  # python-docx
import os

def parse_pdf(file_path):
    doc = fitz.open(file_path)
    structured_elements = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        blocks = page.get_text("blocks")
        for block in blocks:
            text = block[4].strip()
            block_type = block[6] 
            if text and block_type == 0:

                element_type = "paragraph"

                # Heading Detection
                if len(text) < 100:
                    if text.isupper():
                        element_type = "heading"
                    elif text.istitle():
                        element_type = "heading"

                # Table Detection
                lines = text.split("\n")

                if len(lines) >= 3:
                    numeric_count = sum(
                        any(char.isdigit() for char in line)
                        for line in lines
                    )

                    if numeric_count >= len(lines) // 2:
                        element_type = "table"

                structured_elements.append({
                    "element_id": f"pdf_p{page_num + 1}_b{block[5]}",
                    "type": element_type,
                    "page": page_num + 1,
                    "content": text
                })
    doc.close()
    return structured_elements

def parse_docx(file_path):
    doc = docx.Document(file_path)
    structured_elements = []
    for i, para in enumerate(doc.paragraphs):
        text = para.text.strip()
        if text:
            structured_elements.append({
                "element_id": f"docx_b{i}",
                "type": "paragraph",
                "page": 1, # DOCX doesn't have rigid pages, defaulting to 1
                "content": text
            })
    doc.close()
    return structured_elements

def parse_document(file_path):
    """Detects file type and routes to the correct parser."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
        
    ext = file_path.lower().split('.')[-1]
    
    if ext == 'pdf':
        return parse_pdf(file_path)
    elif ext == 'docx':
        return parse_docx(file_path)
    else:
        raise ValueError(f"Unsupported file format: {ext}")