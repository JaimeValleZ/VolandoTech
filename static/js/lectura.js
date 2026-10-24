(function () {
    const $ = (id) => document.getElementById(id);
    const KEY = "lecturaReadingId";
    const hayVoz = "Audio" in window;
    let readingId = null;
    let view = null;
    let story = null;
    let current = 0;

    function show(el, on) {
        el.hidden = !on;
    }

    function setError(message) {
        $("error").textContent = message;
        show($("error"), Boolean(message));
    }

    async function request(method, url, body) {
        const options = { method: method, headers: {} };
        if (body !== undefined) {
            options.headers["Content-Type"] = "application/json";
            options.body = JSON.stringify(body);
        }
        const res = await fetch(url, options);
        const data = await res.json().catch(() => ({}));
        if (!res.ok) {
            const message = typeof data.detail === "string" ? data.detail : "Algo salió mal. Intenta de nuevo.";
            const error = new Error(message);
            error.status = res.status;
            throw error;
        }
        return data;
    }

    function hideReading() {
        ["story", "quiz", "part-done", "loading"].forEach((id) => show($(id), false));
    }

    async function showStart() {
        readingId = null;
        hideReading();
        show($("book"), false);
        const books = await request("GET", "/api/lectura/libros");
        const select = $("book-select");
        select.replaceChildren();
        books.forEach((book) => {
            const option = document.createElement("option");
            option.value = book.id;
            option.textContent = book.title + " (" + book.parts + (book.parts === 1 ? " parte)" : " partes)");
            select.appendChild(option);
        });
        show($("no-books"), books.length === 0);
        show($("start-form"), books.length > 0);
    }

    function renderBook(data) {
        view = data;
        show($("start-form"), false);
        $("book-title").textContent = data.book_title;
        $("book-progress").textContent = data.completed + " de " + data.total + " partes";
        $("progress-fill").style.width = (100 * data.completed / data.total) + "%";
        const list = $("parts");
        list.replaceChildren();
        data.parts.forEach((part) => {
            const item = document.createElement("li");
            const button = document.createElement("button");
            button.type = "button";
            button.className = "part-btn" + (part.done ? " is-done" : part.unlocked ? " is-current" : "");
            button.disabled = !part.unlocked;
            const mark = part.done ? "✓" : part.unlocked ? "▶" : "🔒";
            const name = part.story_title ? part.title + " · " + part.story_title : part.title;
            button.textContent = mark + "  " + name;
            button.addEventListener("click", () => openPart(part.index));
            item.appendChild(button);
            list.appendChild(item);
        });
        show($("book"), true);
    }

    async function refreshBook() {
        renderBook(await request("GET", "/api/lectura/sesiones/" + encodeURIComponent(readingId)));
    }

    async function openPart(index) {
        setError("");
        hideReading();
        show($("book"), false);
        show($("loading"), true);
        try {
            story = await request("POST", "/api/lectura/sesiones/" + encodeURIComponent(readingId) + "/partes/" + index);
            renderStory();
        } catch (error) {
            setError(error.message);
            show($("book"), true);
        } finally {
            show($("loading"), false);
        }
    }

    function renderStory() {
        $("part-label").textContent = "Parte " + (story.part + 1) + " de " + story.total + " · " + story.part_title;
        $("story-title").textContent = story.title;
        const box = $("story-text");
        box.replaceChildren();
        story.text.split(/\n\s*\n/).forEach((paragraph) => {
            const p = document.createElement("p");
            p.textContent = paragraph.trim();
            box.appendChild(p);
        });
        show($("story"), true);
        show($("listen"), hayVoz);
        show($("quiz"), true);
        showQuestion(0);
        $("story").scrollIntoView({ block: "start", behavior: "smooth" });
    }

    function showQuestion(index) {
        current = index;
        $("progress").textContent = "Pregunta " + (index + 1) + " de " + story.questions.length;
        $("question").textContent = story.questions[index].question;
        show($("listen-question"), hayVoz);
        ["feedback", "hint", "explanation", "next", "part-done"].forEach((id) => show($(id), false));
        show($("answer-form"), true);
        $("answer").value = "";
        $("answer").focus();
    }

    function finishQuestion(result) {
        $("feedback").textContent = result.feedback;
        show($("feedback"), true);
        if (result.explanation) {
            $("explanation").textContent = result.explanation;
            show($("explanation"), true);
        }
        if (result.hint && !result.finished) {
            $("hint").textContent = "Pista: " + result.hint;
            show($("hint"), true);
        }
        if (!result.finished) {
            $("answer").value = "";
            $("answer").focus();
            return;
        }
        show($("answer-form"), false);
        if (!result.part_done) {
            show($("next"), true);
            return;
        }
        const last = story.part === story.total - 1;
        $("part-done-text").textContent = last
            ? "¡Terminaste el libro completo! ⭐⭐⭐"
            : "¡Terminaste la parte " + (story.part + 1) + "! ⭐";
        show($("next-part"), !last);
        show($("part-done"), true);
    }

    $("start-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        setError("");
        try {
            const data = await request("POST", "/api/lectura/sesiones", {
                nickname: $("nickname").value.trim(),
                age: Number($("age").value),
                document_id: Number($("book-select").value),
            });
            readingId = data.reading_id;
            localStorage.setItem(KEY, readingId);
            renderBook(data);
            openPart(data.completed < data.total ? data.completed : 0);
        } catch (error) {
            setError(error.message);
        }
    });

    $("answer-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        const answer = $("answer").value.trim();
        if (!answer || !story) return;
        setError("");
        try {
            const result = await request("POST", "/api/lectura/sesiones/" + encodeURIComponent(readingId) + "/responder", {
                story_id: story.story_id,
                question_index: current,
                answer: answer,
            });
            finishQuestion(result);
        } catch (error) {
            // 409: el servidor se reinició y olvidó la parte abierta; se vuelve a abrir.
            if (error.status === 409) {
                openPart(story.part);
                return;
            }
            setError(error.message);
        }
    });

    $("next").addEventListener("click", () => showQuestion(current + 1));
    $("next-part").addEventListener("click", () => openPart(story.part + 1));

    $("back").addEventListener("click", async () => {
        hideReading();
        try {
            await refreshBook();
        } catch (error) {
            setError(error.message);
        }
    });

    $("listen").addEventListener("click", () => {
        window.leerEnVoz($("story-title").textContent + ". " + $("story-text").innerText);
    });

    $("listen-question").addEventListener("click", () => {
        window.leerEnVoz($("question").textContent);
    });

    $("restart").addEventListener("click", () => {
        localStorage.removeItem(KEY);
        window.location.reload();
    });

    async function init() {
        const saved = localStorage.getItem(KEY);
        try {
            if (!saved) {
                await showStart();
                return;
            }
            readingId = saved;
            await refreshBook();
        } catch (error) {
            localStorage.removeItem(KEY);
            if (error.status !== 404) setError(error.message);
            showStart().catch((e) => setError(e.message));
        }
    }

    init();
})();
