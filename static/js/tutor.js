(function () {
    const $ = (id) => document.getElementById(id);
    let quiz = null; // { storyId, questions, current }

    function show(el, on) {
        el.hidden = !on;
    }

    function setError(message) {
        $("error").textContent = message;
        show($("error"), Boolean(message));
    }

    function setBusy(busy) {
        $("story-btn").disabled = busy;
        show($("loading"), busy);
    }

    async function postJson(url, body) {
        const res = await fetch(url, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body),
        });
        const data = await res.json().catch(() => ({}));
        if (!res.ok) {
            const message = typeof data.detail === "string" ? data.detail : "Revisa los datos e intenta de nuevo.";
            throw new Error(message);
        }
        return data;
    }

    async function loadStatus() {
        try {
            const res = await fetch("/api/tutor/status");
            const status = await res.json();
            $("mode-note").textContent = status.ai_enabled
                ? "Cuentos nuevos creados con IA (" + status.model + ")."
                : "Modo de ejemplo: aún no hay clave de IA, así que se usan cuentos guardados.";
            show($("mode-note"), true);
        } catch (_) {
            // Si no responde el estado, la app sigue funcionando.
        }
    }

    function renderStory(story) {
        $("story-title").textContent = story.title;
        const box = $("story-text");
        box.replaceChildren();
        story.text.split(/\n\s*\n/).forEach((paragraph) => {
            const p = document.createElement("p");
            p.textContent = paragraph.trim();
            box.appendChild(p);
        });
        show($("story"), true);
        show($("listen"), "Audio" in window);
    }

    function showQuestion(index) {
        const total = quiz.questions.length;
        const item = quiz.questions[index];
        quiz.current = index;
        $("progress").textContent = "Pregunta " + (index + 1) + " de " + total;
        $("question").textContent = item.question;
        ["feedback", "hint", "explanation", "next"].forEach((id) => show($(id), false));
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
        if (result.finished) {
            show($("answer-form"), false);
            const last = quiz.current === quiz.questions.length - 1;
            show($("next"), !last);
            show($("done"), last);
            $("next").textContent = "Siguiente pregunta";
        } else {
            $("answer").value = "";
            $("answer").focus();
        }
    }

    $("story-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        setError("");
        setBusy(true);
        show($("story"), false);
        show($("quiz"), false);
        show($("done"), false);
        try {
            const story = await postJson("/api/tutor/story", {
                age: Number($("age").value),
                interest: $("interest").value.trim(),
            });
            quiz = { storyId: story.story_id, questions: story.questions, current: 0 };
            renderStory(story);
            show($("quiz"), true);
            showQuestion(0);
        } catch (error) {
            setError(error.message);
        } finally {
            setBusy(false);
        }
    });

    $("answer-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        const answer = $("answer").value.trim();
        if (!answer || !quiz) return;
        setError("");
        try {
            const result = await postJson("/api/tutor/answer", {
                story_id: quiz.storyId,
                question_index: quiz.current,
                answer: answer,
            });
            finishQuestion(result);
        } catch (error) {
            setError(error.message);
        }
    });

    $("next").addEventListener("click", () => {
        showQuestion(quiz.current + 1);
    });

    $("listen").addEventListener("click", () => {
        window.leerEnVoz($("story-title").textContent + ". " + $("story-text").innerText);
    });

    loadStatus();
})();
