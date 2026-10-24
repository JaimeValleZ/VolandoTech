import fitz  # pymupdf
from PIL import Image
import io


def pdf_page_to_pil(page, dpi: int = 300):
    """Rasterizar página PDF a imagen PIL para OCR"""
    mat = fitz.Matrix(dpi / 72, dpi / 72)
    pix = page.get_pixmap(matrix=mat)
    img_data = pix.tobytes("png")
    img = Image.open(io.BytesIO(img_data))
    if img.mode != 'RGB':
        img = img.convert('RGB')
    return img
