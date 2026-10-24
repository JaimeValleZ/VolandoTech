import re
import unicodedata

from app.data.db import connect

CHUNK_CHARS = 700
MAX_CHUNK_CHARS = 1000

STOPWORDS = {
    "a", "al", "con", "de", "del", "el", "en", "es", "la", "las", "le", "les", "lo", "los",
    "me", "mi", "no", "o", "para", "por", "que", "se", "si", "su", "sus", "te", "tu", "un",
    "una", "y", "yo", "muy", "mas", "pero", "como", "cuando", "hay", "son", "ser", "esta",
    "este", "eso", "hacer", "gusta", "gustan", "cosas", "cosa", "mucho", "poco",
}


def _norm(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text.lower())
    return "".join(c for c in decomposed if not unicodedata.combining(c))


def tokens(text: str) -> list:
    return [t for t in re.findall(r"[a-z0-9ñ]+", _norm(text)) if len(t) > 2 and t not in STOPWORDS]


def split_chunks(text: str) -> list:
    """Parte el texto en fragmentos por párrafo, sin pasar de MAX_CHUNK_CHARS."""
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks, current = [], ""
    for paragraph in paragraphs:
        while len(paragraph) > MAX_CHUNK_CHARS:
            cut = paragraph.rfind(" ", 0, MAX_CHUNK_CHARS)
            cut = cut if cut > 0 else MAX_CHUNK_CHARS
            if current:
                chunks.append(current)
                current = ""
            chunks.append(paragraph[:cut].strip())
            paragraph = paragraph[cut:].strip()
        if current and len(current) + len(paragraph) + 2 > CHUNK_CHARS:
            chunks.append(current)
            current = paragraph
        else:
            current = f"{current}\n\n{paragraph}" if current else paragraph
    if current:
        chunks.append(current)
    return chunks


def add_document(title: str, filename: str, text: str, pages: int) -> int:
    chunks = split_chunks(text)
    with connect() as conn:
        cursor = conn.execute(
            "INSERT INTO documents (title, filename, pages, char_count) VALUES (?, ?, ?, ?)",
            (title, filename, pages, len(text)),
        )
        document_id = cursor.lastrowid
        conn.executemany(
            "INSERT INTO chunks (document_id, position, text) VALUES (?, ?, ?)",
            [(document_id, i, chunk) for i, chunk in enumerate(chunks)],
        )
    return document_id


def list_documents() -> list:
    with connect() as conn:
        rows = conn.execute(
            """SELECT d.id, d.title, d.filename, d.pages, d.char_count, d.created_at,
                      (SELECT COUNT(*) FROM chunks c WHERE c.document_id = d.id) AS chunk_count
               FROM documents d ORDER BY d.id DESC"""
        ).fetchall()
    return [dict(row) for row in rows]


def delete_document(document_id: int) -> bool:
    with connect() as conn:
        cursor = conn.execute("DELETE FROM documents WHERE id = ?", (document_id,))
        return cursor.rowcount > 0


def search(query: str, limit: int = 4) -> list:
    """Busca fragmentos con más palabras en común con la consulta (sin embeddings)."""
    terms = set(tokens(query))
    if not terms:
        return []
    with connect() as conn:
        rows = conn.execute(
            """SELECT c.text, d.title FROM chunks c JOIN documents d ON d.id = c.document_id"""
        ).fetchall()
    scored = []
    for row in rows:
        words = tokens(row["text"])
        if not words:
            continue
        hits = sum(1 for w in words if w in terms)
        if hits:
            scored.append((hits / (len(words) ** 0.5), row["title"], row["text"]))
    scored.sort(key=lambda item: item[0], reverse=True)
    return [{"title": title, "text": text} for _, title, text in scored[:limit]]
