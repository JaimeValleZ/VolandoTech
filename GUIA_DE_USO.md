# Guía de uso — Tutor de Lectura

Esta guía explica cómo usar la app paso a paso. Para instalarla o publicarla, ver [README.md](README.md).

Abre la dirección de la app en el navegador: la de Render (`https://….onrender.com`) o, en local, **http://127.0.0.1:8000**.

---

## 1. Antes de usarla con niños

Revisa esto primero, con un adulto responsable:

- **Revisa el material de la escuela** que subas. La app no verifica si el contenido es apropiado.
- **Revisa las tutorías antes de que el niño las use.** La IA puede escribir un cuento poco claro, dar una pista que revela la respuesta, o marcar como incorrecta una respuesta correcta. Esto es importante porque la app todavía no tiene revisión docente.
- **Usa solo apodos.** La app no pide nombre completo; no escribas datos personales del niño en las respuestas.
- **Usa un PIN difícil de adivinar** (`ESCUELA_PIN`, en `.env` o en las variables de Render). Con él se puede subir y borrar material.

---

## 2. Barra lateral

A la izquierda está el menú con cuatro secciones:

| Sección | Para qué sirve | Quién la usa |
|---|---|---|
| **Tutoría** | El niño conversa con el tutor y recibe una lectura personalizada | Niños |
| **Cuentos** | Cuentos de práctica por edad, sin entrevista | Niños o docentes |
| **Base de la escuela** | Subir libros y cuentos de la escuela | Docentes |
| **Extraer texto** | Sacar el texto de un archivo, sin guardarlo | Cualquiera |

En celular, el menú está oculto. Toca el botón **☰** de arriba para abrirlo. Se cierra al tocar fuera, al elegir una sección, o con la tecla Escape.

---

## 3. Base de la escuela (para docentes)

Aquí se guardan los materiales que después usa el tutor para preparar las lecturas.

### Subir un material

1. Abre **Base de la escuela**.
2. Escribe el **PIN de la escuela**.
3. Escribe un **título** (opcional). Si lo dejas vacío, se usa el nombre del archivo.
4. Elige el **archivo**. Formatos: PDF, JPG, PNG, WebP, BMP, TIFF, TXT, MD, DOCX y PPTX.
5. Pulsa **Subir y guardar**.

La app lee el texto con OCR, guarda el texto en la base y **borra el archivo original**. Solo queda el texto.

Cuando se guarda, aparece un mensaje verde y el material se muestra en la lista de abajo.

### Borrar un material

En la lista, pulsa **Borrar** en la fila del material. Pide el PIN.

### Mensajes de error

| Mensaje | Qué significa | Qué hacer |
|---|---|---|
| "PIN incorrecto o no configurado" | El PIN no coincide, o no está configurado | Revisar el PIN |
| "Formato no soportado" | El archivo no es de los formatos permitidos | Convertirlo a PDF o imagen |
| "El archivo no tiene texto que se pueda extraer" | Es un escaneo muy borroso o una imagen sin texto | Usar una foto más nítida |

### Consejos para subir material

- Un PDF con texto seleccionable se lee mejor que una foto.
- Si el libro tiene varios capítulos, súbelos como archivos separados. Así es más fácil borrar uno sin perder el resto.
- Los acentos y la ñ pueden leerse mal en algunos escaneos. Revisa el texto en la vista de **Extraer texto** antes de subir un material importante.

---

## 4. Tutoría (para el niño)

### Paso 1: empezar

1. Abre **Tutoría**.
2. Escribe tu **apodo** (puede ser un nombre inventado).
3. Elige tu **edad** (de 5 a 10 años).
4. Pulsa **Empezar**.

### Paso 2: conocer al tutor

El tutor te hace tres preguntas, una a una:

1. ¿Qué te gusta hacer o de qué te gusta hablar?
2. ¿Qué cosas se te hacen fáciles cuando lees, escribes o aprendes?
3. ¿Qué cosas se te hacen difíciles?

Escribe tu respuesta y pulsa **Enviar**. Puedes escribir frases cortas. Cuando termines, aparece un mensaje de agradecimiento.

### Paso 3: preparar la tutoría

Pulsa **Preparar mi tutoría**.

La app prepara un cuento pensado para ti. **Puede tardar unos segundos.** No cierres la página mientras espera.

Si el cuento usa material de la escuela, aparece la etiqueta "Con materiales de la escuela". Si no, aparece "Creada por IA".

### Paso 4: leer y responder

1. Lee el cuento. Si lo prefieres, pulsa **🔊 Escuchar cuento** para que te lo lean. Si no entiendes una pregunta, pulsa **🔊 Escuchar pregunta** junto a ella.
2. Responde la **primera pregunta** en el cuadro de texto y pulsa **Responder**.
3. Si no aciertas, verás una **pista**. Puedes intentarlo otra vez. Tienes **tres intentos** por pregunta.
4. Cuando aciertas, o después del tercer intento, aparece la **explicación**.
5. Pulsa **Siguiente pregunta** para continuar.
6. Al terminar la tercera pregunta, aparece "¡Terminaste tu tutoría!".

No pasa nada si te equivocas. Las pistas son para ayudarte a encontrar la respuesta en el cuento.

### Empezar de nuevo

Pulsa **Empezar de nuevo** al final de la página. Esto borra tu apodo del navegador, para que puedas crear otro perfil.

**Importante:** el perfil y la tutoría siguen guardados en la app. Si vuelves a escribir el mismo apodo, no se recupera la tutoría anterior; se crea un perfil nuevo.

---

## 5. Cuentos (práctica)

Esta sección sirve para practicar sin hacer la entrevista.

1. Abre **Cuentos**.
2. Elige tu **edad**.
3. Escribe un **tema** si quieres (por ejemplo, "dinosaurios" o "el mar"). Es opcional.
4. Pulsa **Crear cuento**.
5. Responde las preguntas igual que en la tutoría.

En la parte de arriba aparece un aviso:

- **"Cuentos nuevos creados con IA (…)"**: la app tiene configurada la clave de la IA.
- **"Modo de ejemplo…"**: falta la clave de la IA (`NVIDIA_API_KEY`) y se muestran cuentos guardados.

Si la IA no responde, la app muestra en silencio uno de los cuentos guardados, y no lo indica. Si notas que los cuentos se repiten, avisa a quien administra la app para que revise la clave de la IA.

---

## 6. Extraer texto (para cualquiera)

Sirve para sacar el texto de un archivo sin guardarlo en la base de la escuela.

1. Abre **Extraer texto**.
2. Elige un archivo.
3. Pulsa **Extraer texto**.
4. Revisa el resultado: el texto completo, el detalle por página y los avisos.
5. Usa **Copiar texto** para llevarlo a otro programa.

Esta sección no pide PIN ni guarda el material.

---

## 7. Problemas comunes

| Lo que pasa | Qué hacer |
|---|---|
| La página no abre | Revisar la dirección. En Render, la primera visita tras un rato sin uso tarda alrededor de un minuto |
| "No pude preparar la tutoría" | Intentar de nuevo. Si sigue, avisar a quien administra la app para que revise la clave de la IA |
| La tutoría tarda mucho | Puede tardar hasta medio minuto. Esperar sin cerrar la página |
| "No pude revisar tu respuesta" | Volver a intentarlo. Si sigue, recargar la página |
| "No encontramos tu perfil" | Pulsar **Empezar de nuevo** y crear el perfil otra vez |
| El cuento no parece adecuado para la edad | Crear otro cuento, y avisar al docente para revisar el material |
| La pista dice la respuesta | Es un error de la app. Avisar al equipo para corregirlo |
| Una respuesta correcta aparece como incorrecta | Es un error de la app. Escribir la respuesta de otra forma o pasar a la siguiente pregunta |

---

## 8. Limitaciones que conviene conocer

- **La evaluación de respuestas no siempre es confiable.** A veces acepta respuestas incorrectas o rechaza correctas.
- **Las pistas pueden revelar la respuesta.** Revisa las tutorías antes de dárselas a un niño.
- **No hay revisión docente automática.** Un adulto debe revisar el material y las tutorías.
- **Los cuentos de práctica y las respuestas en curso se pierden al reiniciar la app.** Las tutorías sí se guardan.
- **Un solo PIN compartido para toda la escuela.** Cualquiera que lo tenga puede subir o borrar material.
- **La lectura en voz alta necesita internet.** Usa la voz de Microsoft Edge; sin conexión, no se escucha.


---

## 9. Glosario

- **Base de la escuela:** material subido por la escuela, que el tutor usa para preparar las lecturas.
- **Tutoría:** lectura personalizada con cuento y preguntas, hecha para un niño.
- **Pista:** ayuda que aparece al fallar. Debería orientar, no dar la respuesta.
- **OCR:** lectura automática del texto de una imagen o un PDF escaneado.
- **PIN:** clave que protege la base de la escuela.
