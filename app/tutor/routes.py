from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from app.core.templating import templates
from app.tutor import ai_client, service
from app.utils.logger import logger

router = APIRouter()


class StoryRequest(BaseModel):
    age: int = Field(ge=5, le=10)
    interest: str = Field("", max_length=60)


class AnswerRequest(BaseModel):
    story_id: str = Field(min_length=1, max_length=64)
    question_index: int = Field(ge=0, le=10)
    answer: str = Field(min_length=1, max_length=300)


@router.get("/tutor", response_class=HTMLResponse)
async def tutor_page(request: Request):
    return templates.TemplateResponse(request, "tutor.html")


@router.get("/api/tutor/status")
async def tutor_status():
    enabled = ai_client.is_enabled()
    return {"ai_enabled": enabled, "model": ai_client.model_name() if enabled else None}


@router.post("/api/tutor/story")
async def tutor_story(body: StoryRequest):
    return await service.create_story(body.age, body.interest.strip())


@router.post("/api/tutor/answer")
async def tutor_answer(body: AnswerRequest):
    try:
        return await service.check_answer(body.story_id, body.question_index, body.answer.strip())
    except KeyError as error:
        if str(error.args[0]) == "story":
            raise HTTPException(status_code=404, detail="El cuento ya no está disponible. Crea uno nuevo.")
        raise HTTPException(status_code=404, detail="Pregunta no encontrada.")
    except Exception as error:
        logger.error(f"Error al revisar la respuesta: {error}")
        raise HTTPException(status_code=503, detail="No pude revisar tu respuesta. Intenta de nuevo.")
