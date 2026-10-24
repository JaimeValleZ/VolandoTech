from PIL import Image
from app.extractors.ocr import ocr_engine
from app.schemas.extraction import PageResult
from app.utils.normalize import normalize_text
from app.utils.logger import logger



def extract_image(file_path: str) -> list:
    logger.info(f"Procesando imagen: {file_path}")
    warnings = []
    
    try:
        img = Image.open(file_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        result = ocr_engine(img)
        if result.txts:
            ocr_texts = [t for t in result.txts if t]
            text_final = normalize_text('\n'.join(ocr_texts))
        else:
            text_final = ""
            warnings.append("No se detectó texto en la imagen")
        
        return [PageResult(
            page_number=1,
            text=text_final,
            method="ocr",
            has_image=True,
            warnings=warnings
        )]
    except Exception as e:
        return [PageResult(
            page_number=1,
            text="",
            method="ocr",
            has_image=True,
            warnings=[f"Error al procesar imagen: {str(e)}"]
        )]
