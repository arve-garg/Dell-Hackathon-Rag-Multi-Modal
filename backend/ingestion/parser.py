import fitz  # PyMuPDF
import docx  # python-docx
import os
os.makedirs("data/images", exist_ok=True)
os.makedirs("data/captions", exist_ok=True)
from .image_caption import generate_image_caption
USE_GEMINI_IMAGE_CAPTIONS =False
def parse_pdf(file_path):
    doc = fitz.open(file_path)
    structured_elements = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        blocks = page.get_text("blocks")
        image_list = page.get_images(full=True)
        print(
            f"Page {page_num + 1} contains "
            f"{len(image_list)} images"
        )

        for img_index, img in enumerate(image_list):

            xref = img[0]

            base_image = doc.extract_image(xref)

            image_bytes = base_image["image"]

            image_ext = base_image["ext"]

            image_path = (
                f"data/images/"
                f"page_{page_num+1}_img_{img_index}.{image_ext}"
            )
            caption_file = image_path + ".txt"
            with open(image_path, "wb") as f:
                f.write(image_bytes)

            caption_file = (
                f"data/captions/"
                f"page_{page_num+1}_img_{img_index}.txt"
            )

            if os.path.exists(caption_file):

                with open(caption_file, "r", encoding="utf-8") as f:
                    caption = f.read()

                print("USING CACHED CAPTION")

            elif USE_GEMINI_IMAGE_CAPTIONS:

                try:

                    caption = generate_image_caption(image_path)

                    with open(caption_file, "w", encoding="utf-8") as f:
                        f.write(caption)

                except Exception as e:

                    print("CAPTION ERROR:", e)

                    caption = (
                        f"Image from page "
                        f"{page_num + 1}, index {img_index}"
                    )

            else:

                caption = (
                    f"Image from page "
                    f"{page_num + 1}, index {img_index}"
                )
            print("\n===== IMAGE CAPTION =====")
            print(caption)
            print("=========================\n")

            structured_elements.append({
                "element_id": f"pdf_p{page_num+1}_img{img_index}",
                "type": "image",
                "page": page_num + 1,
                "content": caption,
                "image_path": image_path
            })
           
        for block in blocks:
            text = block[4].strip()
            block_type = block[6]

            if text and block_type == 0:

                # Skip footer/header/contact junk
                if (
                    "www." in text
                    or "http" in text
                    or "@" in text
                    or "☎" in text
                    or "+91" in text
                ):
                    continue

                element_type = "paragraph"

                # Heading Detection
                if len(text) < 100:
                    if text.isupper():
                        element_type = "heading"
                    elif text.istitle():
                        element_type = "heading"

                # Table Detection
                lines = text.split("\n")

                if len(lines) >= 4:

                    
                    numeric_count = sum(
                        any(char.isdigit() for char in line)
                        for line in lines
                    )
                    avg_line_length = (
                        sum(len(line) for line in lines)
                        / len(lines)
                    )

                    if (numeric_count >= len(lines)*0.7 and avg_line_length < 80):
                        element_type = "table"
                if element_type == "table":
                    print("\n===== TABLE DETECTED =====")
                    print(text[:500])
                    print("==========================")
                structured_elements.append({
                    "element_id": f"pdf_p{page_num + 1}_b{block[5]}",
                    "type": element_type,
                    "page": page_num + 1,
                    "content": text
                })
    for el in structured_elements:

        if el.get("type") == "image":

            print("\n===== IMAGE NODE =====")
            print(el)
            print("======================")
       

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