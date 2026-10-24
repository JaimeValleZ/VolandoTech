"""Cuentos de respaldo escritos a mano. Se usan cuando no hay clave de API de IA."""


def max_words_for_age(age: int) -> int:
    """Promedio máximo de palabras por oración para cada rango de edad."""
    if age <= 6:
        return 9
    if age <= 8:
        return 12
    return 15


def band_for_age(age: int) -> str:
    if age <= 6:
        return "5-6"
    if age <= 8:
        return "7-8"
    return "9-10"

STORIES = [
    {
        "band": "5-6",
        "title": "Luna y su globo rojo",
        "text": (
            "Luna tenía un globo rojo. Era su juguete favorito.\n\n"
            "Un día, el viento sopló fuerte y se lo llevó hacia el cielo. "
            "Luna miró hacia arriba y empezó a llorar.\n\n"
            "Entonces, un pajarito amarillo voló hasta el globo y lo trajo de vuelta. "
            "¡Qué alegría! Luna le dio las gracias con una gran sonrisa."
        ),
        "questions": [
            {
                "question": "¿De qué color era el globo de Luna?",
                "keywords": ["roj"],
                "hints": ["Busca la primera frase del cuento.", "Es el color de las fresas."],
                "explanation": "El globo de Luna era rojo.",
            },
            {
                "question": "¿Qué se llevó el globo hacia el cielo?",
                "keywords": ["viento"],
                "hints": ["Es algo que no puedes ver, pero sientes cuando sopla.", "Mira la segunda parte del cuento."],
                "explanation": "El viento se llevó el globo.",
            },
            {
                "question": "¿Quién trajo el globo de vuelta?",
                "keywords": ["pajar"],
                "hints": ["Es un animal que vuela.", "Era amarillo."],
                "explanation": "Un pajarito amarillo trajo el globo de vuelta.",
            },
        ],
    },
    {
        "band": "7-8",
        "title": "Mateo y la tortuga del parque",
        "text": (
            "Mateo llegó al parque con su bicicleta. En el camino vio una tortuga que caminaba "
            "muy despacio cerca de la calle.\n\n"
            "Los carros pasaban rápido. Mateo pensó que alguien podría asustarla o pisarla. "
            "Entonces la levantó con cuidado y la llevó al pasto, bajo un árbol grande.\n\n"
            "La tortuga movió la cabeza, como si dijera gracias. Mateo sonrió y siguió pedaleando, "
            "contento de haber ayudado."
        ),
        "questions": [
            {
                "question": "¿Qué vio Mateo en el camino?",
                "keywords": ["tortuga"],
                "hints": ["Busca el animal que caminaba muy despacio.", "Está en la primera parte del cuento."],
                "explanation": "Mateo vio una tortuga que caminaba cerca de la calle.",
            },
            {
                "question": "¿Por qué Mateo decidió mover a la tortuga?",
                "keywords": ["calle", "carro", "rapid", "pis", "asust", "peligr"],
                "hints": ["Piensa en dónde estaba la tortuga.", "Fíjate en lo que pensó Mateo."],
                "explanation": "Estaba cerca de la calle, y podía ser pisada o asustada por los carros.",
            },
            {
                "question": "¿Cómo se sintió Mateo después de ayudar?",
                "keywords": ["bien", "feliz", "alegr", "content", "orgull"],
                "hints": ["Mira la última frase del cuento.", "¿Cómo se siente alguien que sonríe?"],
                "explanation": "Mateo se sintió contento y bien por haber ayudado.",
            },
        ],
    },
    {
        "band": "9-10",
        "title": "La biblioteca del barrio",
        "text": (
            "Cada sábado, Valentina visitaba la biblioteca de su barrio. Un día notó que el cartel "
            "de la entrada estaba roto y que muchos libros estaban desordenados en los estantes.\n\n"
            "Preguntó a la bibliotecaria, la señora Rosa, si podía ayudar. Juntas reorganizaron los "
            "libros por colores y por temas. Después, Valentina escribió un cartel nuevo con letras "
            "grandes: «Bienvenidos, lectores».\n\n"
            "Al final del día, el lugar parecía otro y varios vecinos se quedaron a leer. Valentina "
            "comprendió que cuidar un espacio compartido también es una forma de compartir."
        ),
        "questions": [
            {
                "question": "¿Qué notó Valentina en la biblioteca?",
                "keywords": ["roto", "desorden"],
                "hints": ["Lee la primera parte del cuento.", "Hay dos problemas: uno con el cartel y otro con los libros."],
                "explanation": "Notó que el cartel estaba roto y que los libros estaban desordenados.",
            },
            {
                "question": "¿Cómo ayudó Valentina a la bibliotecaria?",
                "keywords": ["ordena", "reorden", "organiz", "cartel"],
                "hints": ["Lee la parte donde juntas trabajaron.", "También escribió algo nuevo."],
                "explanation": "Reorganizó los libros y escribió un cartel nuevo.",
            },
            {
                "question": "¿Qué quiere decir que cuidar un espacio compartido es una forma de compartir?",
                "keywords": ["todos", "vecin", "otros", "demas", "beneficia", "comunidad"],
                "hints": ["Piensa en quién usa la biblioteca.", "¿Quiénes se quedaron a leer al final?"],
                "explanation": "Cuidar algo que usan todas las personas es una manera de compartirlo con los demás.",
            },
        ],
    },
]
