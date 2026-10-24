import json
import uuid

from app.data.db import connect
from app.kb import service as kb
from app.tutor import ai_client
from app.tutor import service as tutor
from app.utils.logger import logger

# Preguntas de la entrevista inicial, en el orden en que se hacen.
INTERVIEW = [
    ("likes", "¡Hola! Vamos a conocernos 🎈 ¿Qué te gusta hacer o de qué te gusta hablar?"),
    ("easy", "¡Qué bien! ¿Qué cosas se te hacen fáciles cuando lees, escribes o aprendes?"),
    ("hard", "Gracias. ¿Y qué cosas se te hacen difíciles? No pasa nada si son muchas 🙂"),
]
DONE_MESSAGE = "¡Gracias! Ya tengo lo que necesito para preparar tu tutoría. Toca el botón de abajo ⭐"


def _next_question(student: dict) -> str | None:
    for field, question in INTERVIEW:
        if not student[field]:
            return question
    return None


def create_student(nickname: str, age: int) -> dict:
    student_id = uuid.uuid4().hex
    with connect() as conn:
        conn.execute(
            "INSERT INTO students (id, nickname, age) VALUES (?, ?, ?)",
            (student_id, nickname, age),
        )
    return get_student(student_id)


def get_student(student_id: str) -> dict | None:
    with connect() as conn:
        row = conn.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
    return dict(row) if row else None


def student_view(student: dict) -> dict:
    question = _next_question(student)
    plan = json.loads(student["plan_json"]) if student["plan_json"] else None
    return {
        "student_id": student["id"],
        "nickname": student["nickname"],
        "age": student["age"],
        "answers": {field: student[field] for field, _ in INTERVIEW},
        "next_question": question,
        "ready": question is None,
        "has_plan": plan is not None,
    }


def chat(student: dict, message: str) -> dict:
    """Guarda la respuesta a la pregunta actual y devuelve la siguiente pregunta."""
    current = _next_question(student)
    if current is None:
        return {"reply": DONE_MESSAGE, "done": True}
    field = next(f for f, q in INTERVIEW if q == current)
    with connect() as conn:
        conn.execute(f"UPDATE students SET {field} = ? WHERE id = ?", (message, student["id"]))
    student[field] = message
    following = _next_question(student)
    if following is None:
        return {"reply": DONE_MESSAGE, "done": True}
    return {"reply": following, "done": False}


async def prepare(student: dict) -> dict:
    if _next_question(student) is not None:
        raise ValueError("La entrevista aún no está completa.")
    query = f"{student['likes']} {student['hard']}"
    excerpts = kb.search(query)
    data = await ai_client.generate_plan(
        student["age"], student["likes"], student["easy"], student["hard"], excerpts
    )
    if not tutor.valid_generated(data, student["age"]):
        raise RuntimeError("El modelo no generó una tutoría con el nivel adecuado")
    record = tutor.record_from_ai(data)
    record["source"] = "ia+escuela" if excerpts else "ia"
    story_id = tutor.remember(record)
    saved = {
        "story_id": story_id,
        "title": record["title"],
        "text": record["text"],
        "source": record["source"],
        "questions": record["questions"],
    }
    with connect() as conn:
        conn.execute("UPDATE students SET plan_json = ? WHERE id = ?", (json.dumps(saved), student["id"]))
    logger.info(f"Tutoría preparada para {student['nickname']} ({record['source']})")
    return tutor.public_story(story_id, record)


def current_plan(student: dict) -> dict | None:
    if not student["plan_json"]:
        return None
    saved = json.loads(student["plan_json"])
    record = {k: saved[k] for k in ("title", "text", "source", "questions")}
    tutor.ensure_record(saved["story_id"], record)
    return tutor.public_story(saved["story_id"], record)


async def answer(student: dict, question_index: int, answer_text: str) -> dict:
    if not student["plan_json"]:
        raise KeyError("plan")
    story_id = json.loads(student["plan_json"])["story_id"]
    current_plan(student)  # asegura que el cuento esté en memoria
    return await tutor.check_answer(story_id, question_index, answer_text)
