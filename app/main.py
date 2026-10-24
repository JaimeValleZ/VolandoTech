import uuid
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.concurrency import run_in_threadpool
from app.core.config import UPLOAD_DIR, STATIC_DIR, ALLOWED_EXTENSIONS
from app.core.templating import templates
from app.services.extraction_service import ExtractionService
from app.utils.filetype import is_allowed_file
from app.data.db import init_db
from app.kb.service import add_examples_if_empty
from app.kb.routes import router as kb_router
from app.lectura.routes import router as lectura_router
from app.voz.routes import router as voz_router
from app.tutor.routes import router as tutor_router
from app.tutoria.routes import router as tutoria_router
from app.utils.logger import logger

app = FastAPI(title="Tutor de Lectura", version="1.0.0")

# Montar estáticos y templates
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.include_router(tutor_router)
app.include_router(tutoria_router)
app.include_router(lectura_router)
app.include_router(voz_router)
app.include_router(kb_router)
init_db()
if add_examples_if_empty():
    logger.info("Base vacía: se cargaron los libros de ejemplo")


@app.get("/health")
async def health():
    """Respuesta liviana para el chequeo de Render y para mantener el servicio despierto."""
    return {"ok": True}


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request, "home.html")


@app.get("/extraer", response_class=HTMLResponse)
async def extraer(request: Request):
    return templates.TemplateResponse(request, "extraer.html")


@app.post("/upload", response_class=HTMLResponse)
async def upload_file(request: Request, file: UploadFile = File(...)):
    try:
        if not file.filename:
            return templates.TemplateResponse(request, "extraer.html", {
                "error": "No se seleccionó ningún archivo"
            })
        
        if not is_allowed_file(file.filename):
            return templates.TemplateResponse(request, "extraer.html", {
                "error": f"Formato no soportado. Extensiones permitidas: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
            })
        
        # Archivo temporal para extraer el texto
        ext = Path(file.filename).suffix.lower()
        unique_filename = f"{uuid.uuid4()}{ext}"
        file_path = UPLOAD_DIR / unique_filename
        
        file_path.write_bytes(await file.read())
        try:
            result = await run_in_threadpool(ExtractionService.extract, str(file_path), file.filename)
        finally:
            # Esta sección no guarda material: el archivo se borra apenas se extrae el texto.
            file_path.unlink(missing_ok=True)
        logger.info(f"Texto extraído de {file.filename}")

        return templates.TemplateResponse(request, "result.html", {
            "result": result
        })
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return templates.TemplateResponse(request, "extraer.html", {
            "error": f"Error al procesar archivo: {str(e)}"
        })
