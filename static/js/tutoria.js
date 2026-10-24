(function () {
    const $ = (id) => document.getElementById(id);
    const KEY = "tutoriaStudentId";
    const hayVoz = "Audio" in window;
    let studentId = null;
    let questions = [];
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

    function addMessage(text, who) {
        const bubble = document.createElement("div");
        bubble.className = "bubble bubble-" + who;
        bubble.textContent = text;
        $("messages").appendChild(bubble);
        bubble.scrollIntoView({ block: "end", behavior: "smooth" });
    }

    function showStart() {
        studentId = null;
        ["chat", "ready", "story", "quiz", "done"].forEach((id) => show($(id), false));
        show($("start-form"), true);
    }

    function showChat(nextQuestion) {
        show($("start-form"), false);
        show($("chat"), true);
        if (nextQuestion) {
            addMessage(nextQuestion, "bot");
            $("message").focus();
        }
    }

    function renderStory(story) {
        $("story-title").textContent = story.title;
        $("source").textContent = story.source === "ia+escuela" ? "Con materiales de la escuela" : "Creada por IA";
        const box = $("story-text");
        box.replaceChildren();
        story.text.split(/\n\s*\n/).forEach((paragraph) => {
            const p = document.createElement("p");
            p.textContent = paragraph.trim();
            box.appendChild(p);
        });
        show($("story"), true);
        show($("listen"), hayVoz);
        questions = story.questions;
        show($("quiz"), true);
        showQuestion(0);
    }

    function showQuestion(index) {
        current = index;
        $("progress").textContent = "Pregunta " + (index + 1) + " de " + questions.length;
        $("question").textContent = questions[index].question;
        show($("listen-question"), hayVoz);
        ["feedback", "hint", "explanation", "next", "done"].forEach((id) => show($(id), false));
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
            const last = current === questions.length - 1;
            show($("next"), !last);
            show($("done"), last);
        } else {
            $("answer").value = "";
            $("answer").focus();
        }
    }

    async function loadStudent(id) {
        const view = await request("GET", "/api/tutoria/estudiantes/" + encodeURIComponent(id));
        studentId = view.student_id;
        if (view.plan) {
            show($("chat"), false);
            show($("ready"), false);
            renderStory(view.plan);
        } else if (view.ready) {
            show($("chat"), false);
            show($("ready"), true);
        } else {
            showChat(view.next_question);
        }
    }

    $("start-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        setError("");
        try {
            const view = await request("POST", "/api/tutoria/estudiantes", {
                nickname: $("nickname").value.trim(),
                age: Number($("age").value),
            });
            localStorage.setItem(KEY, view.student_id);
            studentId = view.student_id;
            showChat(view.next_question);
        } catch (error) {
            setError(error.message);
        }
    });

    $("chat-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        const message = $("message").value.trim();
        if (!message || !studentId) return;
        setError("");
        addMessage(message, "user");
        $("message").value = "";
        try {
            const result = await request("POST", "/api/tutoria/chat", { student_id: studentId, message: message });
            addMessage(result.reply, "bot");
            if (result.done) {
                show($("chat-form"), false);
                show($("ready"), true);
            }
        } catch (error) {
            setError(error.message);
        }
    });

    $("prepare").addEventListener("click", async () => {
        setError("");
        $("prepare").disabled = true;
        show($("prepare-note"), true);
        try {
            const story = await request("POST", "/api/tutoria/preparar", { student_id: studentId });
            show($("ready"), false);
            renderStory(story);
        } catch (error) {
            setError(error.message);
            $("prepare").disabled = false;
        } finally {
            show($("prepare-note"), false);
        }
    });

    $("answer-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        const answer = $("answer").value.trim();
        if (!answer || !studentId) return;
        setError("");
        try {
            const result = await request("POST", "/api/tutoria/responder", {
                student_id: studentId,
                question_index: current,
                answer: answer,
            });
            finishQuestion(result);
        } catch (error) {
            setError(error.message);
        }
    });

    $("next").addEventListener("click", () => showQuestion(current + 1));

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
        if (!saved) {
            showStart();
            return;
        }
        try {
            await loadStudent(saved);
        } catch (error) {
            localStorage.removeItem(KEY);
            showStart();
            if (error.status !== 404) setError(error.message);
        }
    }

    init();
})();
