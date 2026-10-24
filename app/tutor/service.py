import random
import re
import unicodedata
import uuid
from collections import OrderedDict

from app.tutor import ai_client
from app.tutor.library import STORIES, band_for_age, max_words_for_age
from app.utils.logger import logger

MAX_ATTEMPTS = 3
MAX_STORIES_IN_MEMORY = 200
QUESTIONS_PER_STORY = 3

# Historias recientes, en memoria. No se guarda nada del niño en disco.
_stories = OrderedDict()


def _norm(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text.lower())
    return "".join(c for c in decomposed if not unicodedata.combining(c))


def _is_readable(text: str, age: int) -> bool:
    sentences = [s for s in re.split(r"[.!?]+", text) if s.strip()]
    if not sentences:
        return False
    lengths = [len(s.split()) for s in sentences]
    limit = max_words_for_age(age)
    return sum(lengths) / len(lengths) <= limit and max(lengths) <= limit * 2


def _is_valid_generated(data: dict, age: int, max_chars: int = 1500) -> bool:
    if not isinstance(data.get("title"), str) or not isinstance(data.get("text"), str):
        return False
    if not 60 <= len(data["text"]) <= max_chars or not _is_readable(data["text"], age):
        return False
    questions = data.get("questions")
    if not isinstance(questions, list) or len(questions) != QUESTIONS_PER_STORY:
        return False
    return all(
        isinstance(q.get("question"), str)
        and isinstance(q.get("answer"), str)
        and isinstance(q.get("explanation"), str)
        and isinstance(q.get("hints"), list)
        for q in questions
    )


def _record_from_seed(band: str) -> dict:
    seed = random.choice([s for s in STORIES if s["band"] == band])
    return {
        "title": seed["title"],
        "text": seed["text"],
        "source": "respaldo",
        "questions": [
            {
                "question": q["question"],
                "expected": None,
                "keywords": q["keywords"],
                "hints": q["hints"],
                "explanation": q["explanation"],
            }
            for q in seed["questions"]
        ],
        "attempts": {},
        "solved": set(),
    }


def _record_from_ai(data: dict) -> dict:
    return {
        "title": data["title"].strip(),
        "text": data["text"].strip(),
        "source": "ia",
        "questions": [
            {
                "question": q["question"].strip(),
                "expected": q["answer"].strip(),
                "keywords": [],
                "hints": [str(h).strip() for h in q["hints"][:2]],
                "explanation": q["explanation"].strip(),
            }
            for q in data["questions"][:QUESTIONS_PER_STORY]
        ],
        "attempts": {},
        "solved": set(),
    }


def _public_story(story_id: str, record: dict) -> dict:
    return {
        "story_id": story_id,
        "title": record["title"],
        "text": record["text"],
        "source": record["source"],
        "questions": [{"index": i, "question": q["question"]} for i, q in enumerate(record["questions"])],
    }


def _remember(record: dict) -> str:
    story_id = uuid.uuid4().hex
    _stories[story_id] = record
    while len(_stories) > MAX_STORIES_IN_MEMORY:
        _stories.popitem(last=False)
    return story_id


def valid_generated(data: dict, age: int, max_chars: int = 1500) -> bool:
    return _is_valid_generated(data, age, max_chars)


def record_from_ai(data: dict) -> dict:
    return _record_from_ai(data)


def public_story(story_id: str, record: dict) -> dict:
    return _public_story(story_id, record)


def remember(record: dict) -> str:
    return _remember(record)


def is_finished(story_id: str) -> bool:
    """True si ya se cerraron todas las preguntas del cuento (bien contestadas o agotados los intentos)."""
    record = _stories.get(story_id)
    return record is not None and len(record["solved"]) == len(record["questions"])


def ensure_record(story_id: str, record: dict) -> None:
    """Vuelve a cargar en memoria un cuento guardado (p. ej. tras reiniciar el servidor)."""
    if story_id not in _stories:
        record.setdefault("attempts", {})
        record.setdefault("solved", set())
        _stories[story_id] = record


async def create_story(age: int, interest: str) -> dict:
    band = band_for_age(age)
    record = None
    if ai_client.is_enabled():
        try:
            data = await ai_client.generate_story(age, interest)
            if not _is_valid_generated(data, age):
                raise ValueError("el cuento generado no cumple el nivel de lectura")
            record = _record_from_ai(data)
        except Exception as error:
            logger.warning(f"IA no disponible para crear el cuento, uso respaldo: {error}")
    if record is None:
        record = _record_from_seed(band)
    story_id = _remember(record)
    return _public_story(story_id, record)


async def check_answer(story_id: str, question_index: int, answer: str) -> dict:
    record = _stories.get(story_id)
    if record is None:
        raise KeyError("story")
    if not 0 <= question_index < len(record["questions"]):
        raise KeyError("question")
    question = record["questions"][question_index]

    if question_index in record["solved"]:
        return {"correct": True, "finished": True, "feedback": "Ya contestaste esta pregunta.",
                "hint": None, "explanation": question["explanation"]}

    if question["expected"] is None:
        verdict = {
            "correct": any(_norm(k) in _norm(answer) for k in question["keywords"]),
            "feedback": "¡Muy bien!",
        }
    else:
        verdict = await ai_client.judge_answer(record["text"], question["question"], question["expected"], answer)
        verdict = {"correct": bool(verdict.get("correct")), "feedback": str(verdict.get("feedback", ""))}

    if verdict["correct"]:
        record["solved"].add(question_index)
        return {"correct": True, "finished": True, "feedback": verdict["feedback"],
                "hint": None, "explanation": question["explanation"]}

    attempts = record["attempts"].get(question_index, 0) + 1
    record["attempts"][question_index] = attempts
    if attempts >= MAX_ATTEMPTS:
        record["solved"].add(question_index)
        return {"correct": False, "finished": True,
                "feedback": "Esta vez no fue. Aquí tienes la respuesta para seguir leyendo.",
                "hint": None, "explanation": question["explanation"]}

    hint = question["hints"][attempts - 1] if attempts - 1 < len(question["hints"]) else None
    feedback = verdict["feedback"] if question["expected"] is not None else "Casi. Intenta de nuevo."
    return {"correct": False, "finished": False, "feedback": feedback,
            "hint": hint, "explanation": None}
