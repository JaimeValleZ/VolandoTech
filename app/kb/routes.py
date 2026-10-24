import os
import secrets
import uuid
from pathlib import Path

from fastapi import APIRouter, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse
from starlette.concurrency import run_in_threadpool

from app.core.config import ALLOWED_EXTENSIONS, UPLOAD_DIR
from app.core.templating import templates
from app.kb import service
from app.services.extraction_service import ExtractionService
from app.utils.filetype import is_allowed_file
from app.utils.logger import logger

router = APIRouter()


def _pin_ok(pin: str) -> bool:
    expected = os.getenv("ESCUELA_PIN", "").strip()
    return bool(expected) and secrets.compare_digest(pin.strip(), expected)


def _render(request: Request, message: str = "", error: str = "", status: int = 200):
    return templates.TemplateResponse(
        request,
        "escuela.html",
        {
            "message": message,
            "error": error,
            "documents": service.list_documents(),
            "pin_configured": bool(os.getenv("ESCUELA_PIN", "").strip()),
            "allowed": ", ".join(sorted(ALLOWED_EXTENSIONS)),
        },
        status_code=status,
    )


@router.get("/escuela", response_class=HTMLResponse)
async def escuela_page(request: Request):
    return _render(request)


@router.post("/escuela/subir", response_class=HTMLResponse)
async def escuela_upload(
    request: Request,
    pin: str = Form(""),
    title: str = Form(""),
    file: UploadFile = File(...),
):
    if not _pin_ok(pin):
        return _render(request, error="PIN incorrecto o no configurado en .env (ESCUELA_PIN).", status=403)
    if not file.filename or not is_allowed_file(file.filename):
        return _render(request, error="Formato no soportado para la base de conocimientos.", status=400)

    temp_path = UPLOAD_DIR / f"{uuid.uuid4()}{Path(file.filename).suffix.lower()}"
    try:
        temp_path.write_bytes(await file.read())
        result = await run_in_threadpool(ExtractionService.extract, str(temp_path), file.filename)
    except Exception as error:
        logger.error(f"Error al extraer {file.filename}: {error}")
        return _render(request, error=f"No se pudo leer el archivo: {error}", status=500)
    finally:
        # El archivo original no se conserva: solo el texto extraído entra a la base.
        temp_path.unlink(missing_ok=True)

    if not result.full_text.strip():
        return _render(request, error="El archivo no tiene texto que se pueda extraer.", status=422)

    document_title = title.strip()[:120] or Path(file.filename).stem
    service.add_document(document_title, file.filename, result.full_text, result.total_pages)
    logger.info(f"Documento agregado a la base: {document_title} ({result.total_pages} páginas)")
    return _render(request, message=f"«{document_title}» se agregó a la base de conocimientos.")


@router.post("/escuela/borrar/{document_id}", response_class=HTMLResponse)
async def escuela_delete(request: Request, document_id: int, pin: str = Form("")):
    if not _pin_ok(pin):
        return _render(request, error="PIN incorrecto.", status=403)
    if service.delete_document(document_id):
        return _render(request, message="Documento eliminado.")
    return _render(request, error="Ese documento ya no existe.", status=404)
