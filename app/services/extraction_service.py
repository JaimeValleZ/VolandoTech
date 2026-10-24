import time
from pathlib import Path
from app.extractors.registry import get_extractor
from app.schemas.extraction import ExtractionResult
from app.utils.filetype import get_mime_hint


class ExtractionService:
    @staticmethod
    def extract(file_path: str, filename: str) -> ExtractionResult:
        start_time = time.time()
        
        extractor = get_extractor(file_path)
        pages = extractor(file_path)
        
        # Consolidar texto completo
        full_text = "\n\n".join([p.text for p in pages if p.text])
        char_count = len(full_text)
        used_ocr = any(p.method == "ocr" for p in pages)
        
        # Recopilar warnings
        all_warnings = []
        for p in pages:
            all_warnings.extend(p.warnings)
        
        elapsed_ms = int((time.time() - start_time) * 1000)
        
        ext = Path(filename).suffix.lower()
        
        return ExtractionResult(
            filename=filename,
            mime=get_mime_hint(filename),
            extension=ext,
            pages=pages,
            full_text=full_text,
            total_pages=len(pages),
            char_count=char_count,
            used_ocr=used_ocr,
            warnings=all_warnings,
            elapsed_ms=elapsed_ms
        )
