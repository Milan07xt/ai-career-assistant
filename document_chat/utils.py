import os
import pdfplumber
import docx
import logging

logger = logging.getLogger(__name__)

def extract_pages_from_file(file_obj, filename):
    """
    Extracts text page by page. Returns a list of dicts: [{'page_num': 1, 'text': '...'}]
    """
    ext = os.path.splitext(filename.lower())[1]
    pages = []
    
    try:
        if ext == ".pdf":
            # pdfplumber extracts page-by-page
            with pdfplumber.open(file_obj) as pdf:
                for idx, page in enumerate(pdf.pages):
                    content = page.extract_text()
                    if content:
                        pages.append({
                            "page_num": idx + 1,
                            "text": content.strip()
                        })
                        
        elif ext in [".docx", ".doc"]:
            # Word documents don't have hardcoded page numbers, we chunk paragraphs
            doc = docx.Document(file_obj)
            paras = [p.text for p in doc.paragraphs if p.text]
            page_text = []
            page_num = 1
            for p in paras:
                page_text.append(p)
                if len(page_text) >= 5:
                    pages.append({
                        "page_num": page_num,
                        "text": "\n".join(page_text)
                    })
                    page_text = []
                    page_num += 1
            if page_text:
                pages.append({
                    "page_num": page_num,
                    "text": "\n".join(page_text)
                })
                
        else:
            # TXT or fallback
            file_obj.seek(0)
            content = file_obj.read()
            if isinstance(content, bytes):
                try:
                    content = content.decode("utf-8")
                except UnicodeDecodeError:
                    content = content.decode("latin-1")
            
            # Split text by character chunks to simulate pages
            chunk_size = 1500
            for idx in range(0, len(content), chunk_size):
                pages.append({
                    "page_num": (idx // chunk_size) + 1,
                    "text": content[idx:idx + chunk_size].strip()
                })
    except Exception as e:
        logger.error(f"Error extracting pages: {e}")
        pages.append({
            "page_num": 1,
            "text": f"Error parsing document content: {str(e)}"
        })
        
    return pages
