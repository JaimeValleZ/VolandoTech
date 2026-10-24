from pathlib import Path
from app.extractors.pdf_extractor import extract_pdf
from app.extractors.image_extractor import extract_image
from app.extractors.text_extractor import extract_text_file
from app.extractors.office_extractor import extract_office


def get_extractor(file_path: str):
    ext = Path(file_path).suffix.lower()
    
    if ext == '.pdf':
        return extract_pdf
    elif ext in ['.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff', '.tif']:
        return extract_image
    elif ext in ['.txt', '.md']:
        return extract_text_file
    elif ext in ['.docx', '.pptx']:
        return extract_office
    else:
        raise ValueError(f"Formato no soportado: {ext}")
