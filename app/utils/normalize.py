import re


def normalize_text(text: str) -> str:
    if not text:
        return ""
    # Colapsar espacios múltiples
    text = re.sub(r' +', ' ', text)
    # Colapsar múltiples saltos de línea a máximo 2
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Limpiar espacios al inicio/final de líneas
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(lines)
    return text.strip()
