"""Lectura guiada de un material de la escuela, por capítulos o partes.

Cada parte del libro se cuenta al nivel del niño con la IA y se guarda por rango de edad,
así el siguiente estudiante que lea el mismo libro no espera.
"""
import asyncio
import json
import re
import uuid

from app.data.db import connect
from app.tutor import ai_client
from app.tutor import service as tutor
from app.tutor.library import band_for_age
from app.utils.logger import logger

PART_CHARS = 3500
MIN_PART_CHARS = 200
# Una parte de libro puede ser algo más larga que un cuento suelto (1500).
MAX_ADAPTED_CHARS = 1800
# Si ningún intento cumple el nivel exacto, se acepta uno algo más largo antes que dejar al niño sin leer.
TOLERANT_CHARS = 2200
GENERATION_ATTEMPTS = 3

# Líneas que el OCR deja sueltas: números de página y direcciones web.
NOISE = re.compile(r"^\s*(\d{1,4}|https?://\S+|www\.\S+)\s*$")
NUMBER_WORDS = (
    "primer[oa]?|segund[oa]|tercer[oa]?|cuart[oa]|quint[oa]|sext[oa]|s[eé]ptim[oa]|octav[oa]|"
    "noven[oa]|d[eé]cim[oa]|uno|dos|tres|cuatro|cinco|seis|siete|ocho|nueve|diez"
)
# Encabezados de capítulo: "Capítulo 3", "CAPÍTULO IV", "Parte primera: ...". Los romanos van
# en mayúsculas para no confundir "parte mi..." con un número.
CHAPTER = re.compile(
    rf"^[ \t]*(?i:cap[ií]tulo|parte)[ \t]+(?:\d+|[IVXLC]+|(?i:{NUMBER_WORDS}))\b[^\n]{{0,60}}$",
    re.MULTILINE,
)

class LockedPart(Exception):
    """El niño intenta abrir una parte sin terminar la anterior."""


# Partes que se están generando, para no pedir la misma dos veces a la vez.
_inflight = {}
# Cuento abierto -> (lectura, parte), para saber qué parte avanza al terminar las preguntas.
_open_parts = {}


def _clean(text: str) -> str:
    return "\n".join(line for line in text.splitlines() if not NOISE.match(line)).strip()


def _by_size(text: str) -> list:
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    pieces, current = [], ""
    for paragraph in paragraphs:
        if current and len(current) + len(paragraph) > PART_CHARS:
            pieces.append(current)
            current = paragraph
        else:
            current = f"{current}\n\n{paragraph}" if current else paragraph
    if current:
        pieces.append(current)
    # Un final muy corto se une a la parte anterior.
    if len(pieces) > 1 and len(pieces[-1]) < PART_CHARS // 3:
        pieces[-2] += "\n\n" + pieces.pop()
    return pieces


def split_parts(text: str) -> list:
    """Divide el libro por capítulos si los tiene; si no, en partes de tamaño parecido."""
    text = _clean(text)
    marks = list(CHAPTER.finditer(text))
    if len(marks) < 2:
        return [{"title": f"Parte {i + 1}", "text": piece} for i, piece in enumerate(_by_size(text))]

    parts = []
    intro = text[:marks[0].start()].strip()
    if len(intro) >= PART_CHARS // 3:
        parts.append({"title": "Inicio", "text": intro})
    for i, mark in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(text)
        body = text[mark.end():end].strip()
        # Un encabezado sin texto suele venir del índice del libro.
        if len(body) < MIN_PART_CHARS:
            continue
        heading = " ".join(mark.group(0).split())
        pieces = _by_size(body)
        for j, piece in enumerate(pieces):
            title = heading if len(pieces) == 1 else f"{heading} ({j + 1}/{len(pieces)})"
            parts.append({"title": title, "text": piece})
    return parts


def _document(document_id: int) -> dict | None:
    with connect() as conn:
        row = conn.execute("SELECT id, title FROM documents WHERE id = ?", (document_id,)).fetchone()
        if row is None:
            return None
        chunks = conn.execute(
            "SELECT text FROM chunks WHERE document_id = ? ORDER BY position", (document_id,)
        ).fetchall()
    return {"id": row["id"], "title": row["title"], "parts": split_parts("\n\n".join(c["text"] for c in chunks))}


def list_books() -> list:
    with connect() as conn:
        ids = [row["id"] for row in conn.execute("SELECT id FROM documents ORDER BY id DESC")]
    books = []
    for document_id in ids:
        book = _document(document_id)
        if book and book["parts"]:
            books.append({"id": book["id"], "title": book["title"], "parts": len(book["parts"])})
    return books


def _cached(document_id: int, band: str, position: int) -> dict | None:
    with connect() as conn:
        row = conn.execute(
            "SELECT data_json FROM part_cache WHERE document_id = ? AND band = ? AND position = ?",
            (document_id, band, position),
        ).fetchone()
    return json.loads(row["data_json"]) if row else None


async def _generate(book: dict, age: int, position: int) -> dict:
    band = band_for_age(age)
    previous = _cached(book["id"], band, position - 1) if position else None
    part = book["parts"][position]
    data, fallback = None, None
    for attempt in range(GENERATION_ATTEMPTS):
        try:
            candidate = await ai_client.generate_part(
                age, book["title"], part["title"], position + 1, len(book["parts"]),
                part["text"], (previous or {}).get("summary", ""),
            )
        except ValueError as error:  # JSON mal formado: se vuelve a pedir
            logger.warning(f"Parte {position + 1}, intento {attempt + 1}: {error}")
            continue
        if isinstance(candidate.get("questions"), list):
            candidate["questions"] = candidate["questions"][:tutor.QUESTIONS_PER_STORY]
        if tutor.valid_generated(candidate, age, MAX_ADAPTED_CHARS):
            data = candidate
            break
        logger.warning(f"Parte {position + 1}, intento {attempt + 1}: no cumple el nivel de lectura")
        # Nivel tolerante: oraciones como las de dos años más (el límite ya es el máximo a partir de 9).
        if fallback is None and tutor.valid_generated(candidate, age + 2, TOLERANT_CHARS):
            fallback = candidate
    data = data or fallback
    if data is None:
        raise RuntimeError("El modelo no adaptó la parte con el nivel adecuado")
    data["summary"] = str(data.get("summary", "")).strip()
    with connect() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO part_cache (document_id, band, position, data_json) VALUES (?, ?, ?, ?)",
            (book["id"], band, position, json.dumps(data, ensure_ascii=False)),
        )
    logger.info(f"Parte {position + 1} de «{book['title']}» adaptada para {band} años")
    return data


def _start_generation(book: dict, age: int, position: int) -> asyncio.Task:
    key = (book["id"], band_for_age(age), position)
    task = _inflight.get(key)
    if task is None:
        task = asyncio.create_task(_generate(book, age, position))
        _inflight[key] = task

        def _done(finished: asyncio.Task) -> None:
            _inflight.pop(key, None)
            if not finished.cancelled() and finished.exception():
                logger.warning(f"No se pudo adaptar la parte {position + 1}: {finished.exception()}")

        task.add_done_callback(_done)
    return task


async def _part_data(book: dict, age: int, position: int) -> dict:
    cached = _cached(book["id"], band_for_age(age), position)
    if cached:
        return cached
    # shield: si el niño cierra la página, la parte se sigue generando para la próxima vez.
    return await asyncio.shield(_start_generation(book, age, position))


def create_reading(nickname: str, age: int, document_id: int) -> dict | None:
    if _document(document_id) is None:
        return None
    reading_id = uuid.uuid4().hex
    with connect() as conn:
        conn.execute(
            "INSERT INTO readings (id, nickname, age, document_id) VALUES (?, ?, ?, ?)",
            (reading_id, nickname, age, document_id),
        )
    return get_reading(reading_id)


def get_reading(reading_id: str) -> dict | None:
    with connect() as conn:
        row = conn.execute("SELECT * FROM readings WHERE id = ?", (reading_id,)).fetchone()
    return dict(row) if row else None


def reading_view(reading: dict) -> dict | None:
    book = _document(reading["document_id"])
    if book is None:
        return None
    band = band_for_age(reading["age"])
    parts = []
    for i, part in enumerate(book["parts"]):
        cached = _cached(book["id"], band, i)
        parts.append({
            "index": i,
            "title": part["title"],
            "story_title": cached["title"] if cached else None,
            "done": i < reading["completed"],
            "unlocked": i <= reading["completed"],
        })
    return {
        "reading_id": reading["id"],
        "nickname": reading["nickname"],
        "age": reading["age"],
        "book_title": book["title"],
        "completed": min(reading["completed"], len(parts)),
        "total": len(parts),
        "parts": parts,
    }


async def open_part(reading: dict, position: int) -> dict:
    book = _document(reading["document_id"])
    if book is None:
        raise KeyError("book")
    if not 0 <= position < len(book["parts"]):
        raise KeyError("part")
    if position > reading["completed"]:
        raise LockedPart("Primero termina la parte anterior.")
    data = await _part_data(book, reading["age"], position)
    # Se adelanta la siguiente parte mientras el niño lee esta.
    following = position + 1
    if following < len(book["parts"]) and not _cached(book["id"], band_for_age(reading["age"]), following):
        _start_generation(book, reading["age"], following)

    record = tutor.record_from_ai(data)
    record["source"] = "escuela"
    story_id = tutor.remember(record)
    _open_parts[story_id] = (reading["id"], position)
    story = tutor.public_story(story_id, record)
    story.update({"part": position, "total": len(book["parts"]), "part_title": book["parts"][position]["title"]})
    return story


async def answer(reading: dict, story_id: str, question_index: int, answer_text: str) -> dict:
    if _open_parts.get(story_id) is None or _open_parts[story_id][0] != reading["id"]:
        raise KeyError("story")
    position = _open_parts[story_id][1]
    result = await tutor.check_answer(story_id, question_index, answer_text)
    result["part_done"] = tutor.is_finished(story_id)
    if result["part_done"] and position == reading["completed"]:
        with connect() as conn:
            conn.execute("UPDATE readings SET completed = ? WHERE id = ?", (position + 1, reading["id"]))
        reading["completed"] = position + 1
    result["completed"] = reading["completed"]
    return result
