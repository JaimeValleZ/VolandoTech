# Tutor de Lectura

Aplicación web para niños de 5 a 10 años en Latinoamérica. Una escuela sube sus cuentos y libros (por OCR); el tutor conoce al estudiante con unas preguntas y prepara lecturas a su medida, con preguntas de comprensión y pistas. La IA es la API de NVIDIA y la lectura en voz alta usa Microsoft Edge TTS.

Para la presentación del proyecto, ver [PITCH.md](PITCH.md). Para usarla paso a paso, ver [GUIA_DE_USO.md](GUIA_DE_USO.md).

## Páginas
- **/**: inicio, con el resumen de la app y accesos a cada sección.
- **/tutoria**: el tutor pregunta al niño qué le gusta, qué se le facilita y qué se le dificulta, y prepara una lectura con preguntas.
- **/lectura**: lee un libro de la escuela por capítulos o partes, adaptado a la edad del niño.
- **/tutor**: cuentos de práctica por edad y tema.
- **/escuela**: sube materiales (PDF, imágenes, DOCX, PPTX, TXT, MD). Se extrae el texto, se guarda en la base y el archivo original se borra. Requiere el PIN de la escuela.
- **/extraer**: extrae el texto de un archivo sin guardarlo.

## Ejecutar en local
Requiere Python 3.12.
```
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env      # y completa NVIDIA_API_KEY y ESCUELA_PIN
python run.py
```
Abrir http://127.0.0.1:8000

## Configuración
En local van en `.env`; en Render, en las variables de entorno del servicio. **Nunca subas `.env` a GitHub** (ya está en `.gitignore`).

| Variable | Obligatoria | Para qué |
|---|---|---|
| `NVIDIA_API_KEY` | Sí | Clave de la IA. Gratuita en https://build.nvidia.com |
| `ESCUELA_PIN` | Sí | PIN para subir o borrar materiales. Usa uno difícil de adivinar |
| `NVIDIA_MODEL` | No | Modelo de texto. Por defecto `nvidia/nemotron-3.5-lightning-30b-a3b` |
| `TTS_VOICE` | No | Voz. Por defecto `es-CO-SalomeNeural` (Colombia, mujer) |
| `ESCUELA_NOMBRE` | No | Nombre que aparece en la barra lateral |
| `DATA_DIR` | No | Carpeta de la base de datos. Por defecto `data/` |

Sin `NVIDIA_API_KEY`, la sección de cuentos usa cuentos guardados y la tutoría no se puede preparar.

## Publicar en Render
El repositorio incluye [render.yaml](render.yaml), que configura el servicio, y `.python-version`, que fija Python 3.12 (con la versión por defecto de Render, 3.14, algunas dependencias no se instalan).

1. Sube el proyecto a un repositorio de GitHub (el `.gitignore` deja fuera `.env`, `.venv`, `node_modules` y `data/`).
2. En Render: **New → Blueprint**, elige el repositorio y confirma.
3. Render pide los valores secretos: `NVIDIA_API_KEY` y `ESCUELA_PIN`. Escríbelos ahí; no van en ningún archivo.
4. Espera a que termine el despliegue (instala dependencias y descarga los modelos de OCR) y abre la dirección `https://….onrender.com`.

**Importante sobre el plan gratuito:**
- **Los datos no se conservan.** Los materiales de la escuela, los estudiantes y las partes de libros generadas se borran en cada despliegue o reinicio. Para conservarlos hace falta un plan de pago con disco; las instrucciones están comentadas al final de `render.yaml`.
- **El servicio se duerme** tras 15 minutos sin visitas. La primera visita después tarda alrededor de un minuto en responder.

## Estilos con Tailwind
Las clases de Tailwind se compilan a `static/css/tailwind.css`, que ya viene generado: para usar la app no hace falta Node. Solo si cambias clases en `templates/` o `static/js/`, vuelve a compilar:
```
npm install
npm run build:css      # una vez
npm run watch:css      # o en modo vigilancia mientras editas
```
La configuración está en `tailwind.config.js` y la fuente en `static/css/tailwind.src.css`. El reinicio global de Tailwind (preflight) está desactivado para no cambiar los estilos de `styles.css`.

## Privacidad
- No se pide el nombre completo del niño; basta un apodo.
- Los datos del estudiante (apodo, edad y respuestas de la entrevista) se guardan en la base de datos del servidor (`data/tutor.sqlite3`).
- Para generar las lecturas se envían a la API de NVIDIA la edad, los gustos y las respuestas del niño, y fragmentos de los materiales de la escuela.
- Para leer en voz alta se envía el texto del cuento o la pregunta a Microsoft (Edge TTS).
- Los archivos subidos se borran tras extraer el texto; solo queda el texto.
- El identificador del estudiante se guarda en su navegador: quien use ese navegador puede seguir su tutoría.

## Limitaciones actuales
- Una sola escuela por instalación; el PIN es compartido.
- La búsqueda de material usa coincidencia de palabras, sin embeddings.
- La entrevista usa preguntas fijas, no conversación libre con el modelo.
- No hay revisión humana automática del contenido generado: un docente debe revisar los materiales y las tutorías.
