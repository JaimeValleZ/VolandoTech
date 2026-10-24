from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from app.core.templating import templates
from app.lectura import service
from app.utils.logger import logger

router = APIRouter()


class NewReading(BaseModel):
    nickname: str = Field(min_length=1, max_length=30)
    age: int = Field(ge=5, le=10)
    document_id: int


class AnswerRequest(BaseModel):
    story_id: str = Field(min_length=1, max_length=64)
    question_index: int = Field(ge=0, le=10)
    answer: str = Field(min_length=1, max_length=300)


def _reading_or_404(reading_id: str) -> dict:
    reading = service.get_reading(reading_id)
    if reading is None:
        raise HTTPException(status_code=404, detail="No encontramos tu lectura. Elige un libro de nuevo.")
    return reading


@router.get("/lectura", response_class=HTMLResponse)
async def lectura_page(request: Request):
    return templates.TemplateResponse(request, "lectura.html")


@router.get("/api/lectura/libros")
async def books():
    return service.list_books()


@router.post("/api/lectura/sesiones")
async def create_reading(body: NewReading):
    reading = service.create_reading(body.nickname.strip(), body.age, body.document_id)
    if reading is None:
        raise HTTPException(status_code=404, detail="Ese libro ya no está en la base de la escuela.")
    return service.reading_view(reading)


@router.get("/api/lectura/sesiones/{reading_id}")
async def get_reading(reading_id: str):
    view = service.reading_view(_reading_or_404(reading_id))
    if view is None:
        raise HTTPException(status_code=404, detail="Ese libro ya no está en la base de la escuela.")
    return view


@router.post("/api/lectura/sesiones/{reading_id}/partes/{position}")
async def open_part(reading_id: str, position: int):
    reading = _reading_or_404(reading_id)
    try:
        return await service.open_part(reading, position)
    except KeyError:
        raise HTTPException(status_code=404, detail="Esa parte del libro no existe.")
    except service.LockedPart as error:
        raise HTTPException(status_code=400, detail=str(error))
    except Exception as error:
        logger.error(f"No se pudo preparar la parte {position + 1}: {error}")
        raise HTTPException(
            status_code=503,
            detail="No pude preparar esta parte. Revisa la conexión con la IA e inténtalo de nuevo.",
        )


@router.post("/api/lectura/sesiones/{reading_id}/responder")
async def answer(reading_id: str, body: AnswerRequest):
    reading = _reading_or_404(reading_id)
    try:
        return await service.answer(reading, body.story_id, body.question_index, body.answer.strip())
    except KeyError as error:
        if str(error.args[0]) == "question":
            raise HTTPException(status_code=404, detail="Pregunta no encontrada.")
        raise HTTPException(status_code=409, detail="Esta parte se cerró. Ábrela de nuevo para seguir.")
    except Exception as error:
        logger.error(f"Error al revisar la respuesta de lectura: {error}")
        raise HTTPException(status_code=503, detail="No pude revisar tu respuesta. Intenta de nuevo.")
