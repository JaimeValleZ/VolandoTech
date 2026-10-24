from pydantic import BaseModel
from typing import List, Literal


class PageResult(BaseModel):
    page_number: int
    text: str
    method: Literal["text", "ocr", "mixed"]
    has_image: bool
    warnings: List[str] = []


class ExtractionResult(BaseModel):
    filename: str
    mime: str = ""
    extension: str
    pages: List[PageResult]
    full_text: str
    total_pages: int
    char_count: int
    used_ocr: bool
    warnings: List[str] = []
    elapsed_ms: int = 0
