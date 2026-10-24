# Tutor de Lectura

**Un tutor con IA que convierte los libros de la escuela en lecturas a la medida de cada niño, y lo acompaña pregunta a pregunta hasta que entiende lo que lee.**

> Reto: *Tutor de lectura interactivo con IA que acompaña a niños con relatos adaptados a su nivel para cerrar la brecha de comprensión lectora.*

---

## El problema

En Latinoamérica, muchos niños terminan los primeros grados sabiendo *decodificar* (leer en voz alta las palabras) pero sin *comprender* lo que leen. Las evaluaciones regionales e internacionales (ERCE de UNESCO, PISA) lo muestran año tras año.

Tres causas se repiten en el aula:

1. **Un texto para todos.** En un mismo salón hay niños de 7 años que leen como de 5 y otros que leen como de 10, pero todos reciben el mismo libro.
2. **Poco acompañamiento individual.** Un docente con 30 o 40 estudiantes no puede sentarse con cada uno a preguntarle qué entendió, darle una pista y volver a intentar.
3. **Textos que no conectan.** Si al niño no le interesa lo que lee, deja de leer.

## La solución

Tutor de Lectura es una aplicación web que hace tres cosas:

- **Adapta el texto al niño:** a su edad, a sus gustos y a lo que se le dificulta.
- **Usa el material que la escuela ya tiene:** el docente sube sus cuentos y libros (PDF, fotos de páginas impresas, Word, PowerPoint) y la app los convierte en lecturas guiadas.
- **Acompaña la comprensión:** después de cada lectura hace preguntas, da pistas graduadas cuando el niño se equivoca y explica la respuesta al final, como lo haría un tutor sentado a su lado.

---

## Funcionalidades

### 1. Tutoría personalizada
El tutor conversa con el niño y le hace tres preguntas: qué le gusta, qué se le facilita y qué se le dificulta. Con esas respuestas, y con los materiales de la escuela relacionados, la IA escribe una lectura hecha para ese niño.

### 2. Leer un libro de la escuela, por capítulos
El niño elige un libro de la biblioteca de la escuela. La app lo divide automáticamente:
- **por capítulos**, si el libro los tiene ("Capítulo 1", "CAPÍTULO IV", "Parte segunda"…);
- **por partes de tamaño parecido**, si no los tiene.

Cada parte se cuenta al nivel del niño, fiel a la historia original y con los mismos personajes. La app recuerda lo que pasó en la parte anterior para mantener la continuidad. Las partes se desbloquean una a una y una barra muestra el avance del libro.

### 3. Preguntas de comprensión con pistas
Cada lectura trae tres preguntas, cada una de un nivel distinto:
| Tipo | Qué trabaja | Ejemplo |
|---|---|---|
| **Literal** | Encontrar información que está en el texto | ¿Quién encontró el balón rojo? |
| **Inferencial** | Deducir lo que el texto no dice directamente | ¿Por qué las hermanas no querían mudarse al campo? |
| **Vocabulario** | Entender palabras nuevas por el contexto | ¿Qué significa "afligirse"? |

La IA revisa la respuesta del niño con flexibilidad: acepta respuestas parciales, con faltas de ortografía o con otras palabras que digan lo mismo. Si la respuesta no es correcta:
- **no le revela la respuesta**, le da una pista;
- tiene hasta **tres intentos**, con una pista nueva cada vez;
- al final siempre recibe una **explicación**, para que el error también enseñe.

### 4. Lectura en voz alta
Cada texto y cada pregunta se pueden escuchar con una voz neuronal en español de Colombia (Microsoft Edge TTS). La voz lee un poco más despacio de lo normal, pensando en niños que están aprendiendo.

### 5. Cuentos de práctica
Cuentos cortos por edad y por tema ("dinosaurios", "fútbol", "el mar"…) con sus preguntas. Si la IA no está disponible, la app usa cuentos escritos a mano, así nunca se queda sin contenido.

### 6. Base de conocimientos de la escuela
El docente sube materiales protegidos con un PIN. La app extrae el texto con OCR, incluso de fotos de páginas impresas, y **borra el archivo original**: solo se guarda el texto.

Formatos: PDF, JPG, PNG, WEBP, BMP, TIFF, DOCX, PPTX, TXT y MD.

### 7. Extracción de texto
Herramienta para que el docente convierta cualquier documento o imagen en texto editable.

---

## Puntos fuertes

- **El nivel de lectura se mide, no solo se pide.** La app no confía a ciegas en la IA: comprueba que cada texto generado tenga oraciones del largo adecuado para la edad (en promedio, como máximo 9 palabras a los 5–6 años, 12 a los 7–8 y 15 a los 9–10). Si no lo cumple, lo vuelve a pedir.
- **Usa el currículo real de la escuela.** No es una biblioteca genérica: son los cuentos y libros que el docente ya eligió.
- **Lee libros completos, no solo cuentos sueltos.** La lectura por capítulos permite que el niño avance en una obra larga sin perderse, con la continuidad que da el resumen de cada parte.
- **Rápido para la clase.** Mientras el niño lee una parte, la app ya está preparando la siguiente. Lo que se genera se guarda por rango de edad: el siguiente niño de esa edad que lea el mismo libro no espera.
- **Seguro para niños.** Los textos se generan sin violencia, sin miedo intenso y sin datos personales reales. Lo que el niño escribe se trata como una respuesta a evaluar, nunca como una instrucción para la IA.
- **Privado por diseño.** No se pide el nombre completo ni se crean cuentas: basta un apodo. Los archivos subidos se borran después de extraer el texto.
- **De bajo costo.** Usa la API gratuita de NVIDIA para la IA y la voz de Microsoft Edge, y se publica en Render. El modelo se cambia con una línea de configuración.
- **Sirve para escuelas con poca tecnología.** Basta una foto del libro impreso para digitalizarlo. Es una página web: no hay que instalar nada y se usa desde el navegador, incluso en un celular.

---

## En qué nos diferenciamos

| | Chatbot de IA genérico | App de lectura tradicional | **Tutor de Lectura** |
|---|---|---|---|
| Contenido | Lo que el niño pida | Biblioteca fija del proveedor | **Los libros de la propia escuela** |
| Nivel del texto | Sin control | Fijo por libro | **Adaptado a cada niño y verificado** |
| Intereses del niño | No los conoce | No los usa | **Los pregunta y los usa** |
| Libros largos | No | Sí, sin adaptar | **Sí, por capítulos y adaptados** |
| Si el niño se equivoca | Suele dar la respuesta | Marca el error | **Da pistas graduadas y luego explica** |
| Privacidad | Datos en la nube | Cuentas y datos en la nube | **Solo un apodo, sin cuentas** |
| Diseñado para 5–10 años | No | Sí | **Sí** |

En pocas palabras: **no reemplazamos el libro de la escuela, lo hacemos accesible para cada niño.**

---

## Cómo ayuda a mejorar la comprensión lectora

1. **Texto a la medida.** El niño lee un texto que puede entender, con un poco de desafío, ni tan fácil que aburra ni tan difícil que frustre. Esa zona es donde más se aprende.
2. **Motivación por interés.** Cuando la lectura trata de lo que le gusta al niño, lee más y con más atención.
3. **Los tres niveles de comprensión, en cada lectura.** Las preguntas literales, inferenciales y de vocabulario entrenan de forma sistemática las habilidades que las evaluaciones miden y que más cuestan, sobre todo la inferencia.
4. **Andamiaje en vez de corrección.** Las pistas graduadas obligan al niño a volver al texto y buscar, en lugar de recibir la respuesta. La explicación final cierra el aprendizaje.
5. **Vocabulario en contexto.** Cada texto explica una palabra nueva dentro de la historia y luego la pregunta.
6. **Apoyo auditivo.** Escuchar el texto mientras lo sigue con la vista ayuda al niño que todavía decodifica despacio a concentrarse en el significado.
7. **Lectura sostenida.** Leer un libro completo por partes, con progreso visible, construye el hábito y la capacidad de seguir una historia larga.
8. **Más alcance para el docente.** La app atiende a cada niño de forma individual mientras el docente acompaña a quien más lo necesita.

### Cómo mediríamos el impacto en un piloto
- Porcentaje de preguntas correctas al primer intento, por tipo (literal, inferencial, vocabulario), a lo largo de las semanas.
- Número de pistas que necesita cada niño, que debería bajar con el tiempo.
- Partes y libros completados por estudiante.
- Evaluación de comprensión lectora antes y después del piloto, comparando con un grupo sin la app.

---

## Cómo funciona por dentro

- **Backend:** Python + FastAPI, base de datos SQLite. Publicado en Render.
- **OCR:** RapidOCR y PyMuPDF para PDF e imágenes; python-docx y python-pptx para documentos de Office.
- **IA:** API de NVIDIA, modelo Nemotron (gratuito), configurable.
- **Voz:** Microsoft Edge TTS (es-CO-SalomeNeural).
- **Frontend:** HTML, CSS y JavaScript, sin instalación. Funciona en computadora, tablet y celular.

---

## Limitaciones actuales y próximos pasos

Lo que hoy tiene la app y lo que haríamos después:

| Hoy | Próximo paso |
|---|---|
| El modelo gratuito a veces escribe textos más largos de lo pedido; la app reintenta y, si no lo logra, acepta un texto un poco más complejo | Probar modelos más precisos y ajustar los límites con docentes |
| La búsqueda de materiales usa coincidencia de palabras | Búsqueda por significado (embeddings) |
| Una escuela por instalación, con un PIN compartido | Cuentas de docente y varias escuelas |
| No hay panel para el docente | Panel con el avance de cada estudiante y las preguntas que más fallan |
| El contenido generado no tiene revisión humana automática | Flujo para que el docente apruebe las partes antes de publicarlas |
| En el plan gratuito de Render los datos se borran al reiniciar | Disco persistente o base de datos administrada |

---

## Cierre

Cada niño lee a un ritmo distinto, pero hoy casi todos reciben el mismo texto y casi ninguno tiene a alguien que le pregunte qué entendió. **Tutor de Lectura le da a cada niño un tutor paciente que conoce sus gustos, lee con él los libros de su escuela y no le da la respuesta: le enseña a encontrarla.**
