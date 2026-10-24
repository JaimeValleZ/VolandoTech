from pathlib import Path
from app.schemas.extraction import PageResult
from app.utils.normalize import normalize_text
from app.utils.logger import logger


def extract_text_file(file_path: str) -> list:
    logger.info(f"Procesando archivo de texto: {file_path}")
    warnings = []
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        text_final = normalize_text(content)
        if not text_final:
            warnings.append("Archivo vacío")
        return [PageResult(
            page_number=1,
            text=text_final,
            method="text",
            has_image=False,
            warnings=warnings
        )]
    except Exception as e:
        return [PageResult(
            page_number=1,
            text="",
            method="text",
            has_image=False,
            warnings=[f"Error al leer archivo: {str(e)}"]
        )]
