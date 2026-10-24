from fastapi.templating import Jinja2Templates

from app.core.config import APP_NOMBRE, ESCUELA_NOMBRE, STATIC_DIR, TEMPLATES_DIR

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
templates.env.globals["app_nombre"] = APP_NOMBRE
templates.env.globals["escuela_nombre"] = ESCUELA_NOMBRE


def static_url(path: str) -> str:
    """Ruta a un archivo estático con su fecha de cambio, para que el navegador no use una copia vieja."""
    try:
        version = int((STATIC_DIR / path).stat().st_mtime)
    except OSError:
        return f"/static/{path}"
    return f"/static/{path}?v={version}"


templates.env.globals["static_url"] = static_url
