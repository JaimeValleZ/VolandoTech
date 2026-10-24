"""Lectura en voz alta con las voces neuronales de Microsoft Edge (requiere internet).

TTS_VOICE elige la voz; por defecto es-CO-SalomeNeural (español de Colombia, mujer).
El navegador pide un enlace con POST y luego reproduce el audio mientras llega, sin esperar
a que se genere completo.
"""
import os
import uuid
from collections import OrderedDict

import edge_tts
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response, StreamingResponse
from pydantic import BaseModel, Field

from app.utils.logger import logger

router = APIRouter()

DEFAULT_VOICE = "es-CO-SalomeNeural"
# Un poco más lento que lo normal, para niños que empiezan a leer.
RATE = "-10%"
MAX_CACHED = 100

# Textos pedidos, por id del enlace, y audios ya generados por (voz, texto).
_requests = OrderedDict()
_cache = OrderedDict()


class SpeechRequest(BaseModel):
    text: str = Field(min_length=1, max_length=4000)


def _voice() -> str:
    return os.getenv("TTS_VOICE", "").strip() or DEFAULT_VOICE


def _remember(store: OrderedDict, key, value) -> None:
    store[key] = value
    store.move_to_end(key)
    while len(store) > MAX_CACHED:
        store.popitem(last=False)


@router.post("/api/voz")
async def prepare_speech(body: SpeechRequest):
    speech_id = uuid.uuid4().hex
    _remember(_requests, speech_id, (_voice(), body.text.strip()))
    return {"url": f"/api/voz/{speech_id}"}


@router.get("/api/voz/{speech_id}")
async def speak(speech_id: str):
    key = _requests.get(speech_id)
    if key is None:
        raise HTTPException(status_code=404, detail="Audio no encontrado.")
    if key in _cache:
        return Response(content=_cache[key], media_type="audio/mpeg")

    voice, text = key
    stream = edge_tts.Communicate(text, voice, rate=RATE).stream()
    # Se espera el primer fragmento antes de responder: si Edge falla, el navegador recibe
    # un error y usa su propia voz en lugar de quedarse en silencio.
    try:
        first = await _next_audio(stream)
    except Exception as error:
        logger.warning(f"No se pudo generar la voz con Edge TTS: {error}")
        raise HTTPException(status_code=503, detail="La voz no está disponible ahora.")

    async def body():
        audio = bytearray(first)
        yield first
        async for chunk in stream:
            if chunk["type"] == "audio":
                audio.extend(chunk["data"])
                yield chunk["data"]
        _remember(_cache, key, bytes(audio))

    return StreamingResponse(body(), media_type="audio/mpeg")


async def _next_audio(stream) -> bytes:
    async for chunk in stream:
        if chunk["type"] == "audio":
            return chunk["data"]
    raise RuntimeError("Edge TTS no devolvió audio")
