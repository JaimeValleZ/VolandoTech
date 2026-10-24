import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
# En local las variables vienen de .env; en Render, de la configuración del servicio.
load_dotenv(BASE_DIR / ".env")

# DATA_DIR permite guardar la base en un disco persistente del servidor.
DATA_DIR = Path(os.getenv("DATA_DIR", "").strip() or BASE_DIR / "data")
UPLOAD_DIR = DATA_DIR / "uploads"
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

for dir_path in [DATA_DIR, UPLOAD_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {
    '.pdf', '.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff', '.tif',
    '.txt', '.md', '.docx', '.pptx'
}

# Render indica el puerto en PORT y necesita que la app escuche en 0.0.0.0.
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8000"))

APP_NOMBRE = "Tutor de Lectura VT"
ESCUELA_NOMBRE = os.getenv("ESCUELA_NOMBRE", "").strip() or "Escuela demo"
