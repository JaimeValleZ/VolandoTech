import fitz
from pathlib import Path
from app.extractors.ocr import ocr_engine
from app.schemas.extraction import PageResult
from app.utils.images import pdf_page_to_pil
from app.utils.normalize import normalize_text
from app.utils.logger import logger



def extract_pdf(file_path: str) -> list:
    pages_results = []
    doc = fitz.open(file_path)
    total_pages = len(doc)
    
    logger.info(f"Procesando PDF: {total_pages} páginas")
    
    for i, page in enumerate(doc):
        page_num = i + 1
        logger.info(f"Procesando página {page_num} de {total_pages}...")
        warnings = []
        
        # Intentar extraer texto nativo
        text_nativo = page.get_text("text").strip()
        
        if len(text_nativo) > 50:  # Tiene texto suficiente
            text_final = normalize_text(text_nativo)
            method = "text"
            has_image = len(page.get_images()) > 0
            if has_image:
                method = "mixed"
        else:
            # Poca extracción nativa - usar OCR
            logger.info(f"  Página {page_num}: Poco texto nativo, usando OCR...")
            try:
                img = pdf_page_to_pil(page, dpi=300)
                result = ocr_engine(img)
                if result.txts:
                    ocr_texts = [t for t in result.txts if t]
                    text_final = normalize_text('\n'.join(ocr_texts))
                    method = "ocr"
                else:
                    text_final = ""
                    warnings.append("No se pudo extraer texto con OCR")
                has_image = True
            except Exception as e:
                warnings.append(f"Error OCR: {str(e)}")
                text_final = normalize_text(text_nativo) if text_nativo else ""
                method = "text"
                has_image = True
        
        pages_results.append(PageResult(
            page_number=page_num,
            text=text_final,
            method=method,
            has_image=has_image,
            warnings=warnings
        ))
    
    doc.close()
    return pages_results
