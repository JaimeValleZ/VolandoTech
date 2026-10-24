from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from app.core.templating import templates
from app.tutoria import service
from app.utils.logger import logger

router = APIRouter()


class NewStudent(BaseModel):
    nickname: str = Field(min_length=1, max_length=30)
    age: int = Field(ge=5, le=10)


class ChatMessage(BaseModel):
    student_id: str = Field(min_length=1, max_length=64)
    message: str = Field(min_length=1, max_length=300)


class StudentRef(BaseModel):
    student_id: str = Field(min_length=1, max_length=64)


class AnswerRequest(BaseModel):
    student_id: str = Field(min_length=1, max_length=64)
    question_index: int = Field(ge=0, le=10)
    answer: str = Field(min_length=1, max_length=300)


def _student_or_404(student_id: str) -> dict:
    student = service.get_student(student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="No encontramos tu perfil. Empieza de nuevo.")
    return student


@router.get("/tutoria", response_class=HTMLResponse)
async def tutoria_page(request: Request):
    return templates.TemplateResponse(request, "tutoria.html")


@router.post("/api/tutoria/estudiantes")
async def create_student(body: NewStudent):
    student = service.create_student(body.nickname.strip(), body.age)
    return service.student_view(student)


@router.get("/api/tutoria/estudiantes/{student_id}")
async def get_student(student_id: str):
    student = _student_or_404(student_id)
    view = service.student_view(student)
    plan = service.current_plan(student)
    view["plan"] = plan
    return view


@router.post("/api/tutoria/chat")
async def tutoria_chat(body: ChatMessage):
    student = _student_or_404(body.student_id)
    return service.chat(student, body.message.strip())


@router.post("/api/tutoria/preparar")
async def tutoria_prepare(body: StudentRef):
    student = _student_or_404(body.student_id)
    try:
        return await service.prepare(student)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    except Exception as error:
        logger.error(f"No se pudo preparar la tutoría: {error}")
        raise HTTPException(
            status_code=503,
            detail="No pude preparar la tutoría. Revisa la conexión con la IA e inténtalo de nuevo.",
        )


@router.post("/api/tutoria/responder")
async def tutoria_answer(body: AnswerRequest):
    student = _student_or_404(body.student_id)
    try:
        return await service.answer(student, body.question_index, body.answer.strip())
    except KeyError as error:
        if str(error.args[0]) == "plan":
            raise HTTPException(status_code=400, detail="Primero prepara tu tutoría.")
        raise HTTPException(status_code=404, detail="Pregunta no encontrada.")
    except Exception as error:
        logger.error(f"Error al revisar la respuesta de tutoría: {error}")
        raise HTTPException(status_code=503, detail="No pude revisar tu respuesta. Intenta de nuevo.")
