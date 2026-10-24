// Tutorial estilo videojuego: Lumi, el búho lector, presenta cada sección de la app.
// Se abre con el botón "Ver tutorial" del inicio y se puede cerrar en cualquier momento (Salir o Escape).
(function () {
    const start = document.getElementById("tour-start");
    if (!start) return;

    const STEPS = [
        { title: "¡Hola, lector!", text: "Soy Lumi. Te muestro la app en un momento. Puedes salir cuando quieras." },
        { target: "/tutoria", title: "Tutoría", text: "Te hago 3 preguntas sobre lo que te gusta y preparo una lectura solo para ti, con preguntas y pistas." },
        { target: "/lectura", title: "Leer un libro", text: "Lee un libro de tu escuela por partes. Al terminar una, se desbloquea la siguiente." },
        { target: "/tutor", title: "Cuentos", text: "Cuentos cortos del tema que elijas, para practicar. Toca «Escuchar» y te los leo en voz alta." },
        { target: "/escuela", title: "Base de la escuela", text: "Para docentes: suben libros en PDF, fotos o Word, y yo los uso en las lecturas." },
        { target: "/extraer", title: "Extraer texto", text: "Convierte una foto o un documento en texto para copiarlo." },
        { title: "¡Misión cumplida!", text: "Ya conoces toda la app. ¿Empezamos a leer?", final: true },
    ];
    const MOBILE = window.matchMedia("(max-width: 900px)");
    const QUIET = window.matchMedia("(prefers-reduced-motion: reduce)");
    const TYPE_MS = 22;

    // Lumi: búho lector dibujado con los colores del tema.
    const LUMI =
        '<svg viewBox="0 0 64 64" width="64" height="64" aria-hidden="true">' +
        '<path d="M15 14l6 7M49 14l-6 7" stroke="var(--mint-700)" stroke-width="3" stroke-linecap="round"/>' +
        '<ellipse cx="32" cy="32" rx="19" ry="20" fill="var(--mint-400)"/>' +
        '<ellipse cx="32" cy="38" rx="11" ry="11" fill="var(--mint-200)"/>' +
        '<circle cx="24.5" cy="27" r="7" fill="#fff"/><circle cx="39.5" cy="27" r="7" fill="#fff"/>' +
        '<circle cx="25.5" cy="28" r="3.2" fill="#1d1d1f"/><circle cx="40.5" cy="28" r="3.2" fill="#1d1d1f"/>' +
        '<circle cx="26.6" cy="26.8" r="1" fill="#fff"/><circle cx="41.6" cy="26.8" r="1" fill="#fff"/>' +
        '<path d="M29.5 33h5l-2.5 3.5z" fill="#f2a86c"/>' +
        // Libro abierto que Lumi sostiene abajo.
        '<path d="M14 50q9-4 18 0q9-4 18 0v9q-9-4-18 0q-9-4-18 0z" fill="var(--surface)" stroke="var(--mint-700)" stroke-width="2" stroke-linejoin="round"/>' +
        '<path d="M32 50v9M18 53.5q5-1.5 10 0M36 53.5q5-1.5 10 0" stroke="var(--mint-500)" stroke-width="1.5" stroke-linecap="round"/>' +
        "</svg>";

    let index = 0;
    let typing = null;
    let ui = null;
    let openedSidebar = false;

    function build() {
        const root = document.createElement("div");
        root.className = "tour";
        root.innerHTML =
            '<div class="tour-spotlight" aria-hidden="true"></div>' +
            '<div class="tour-bubble" role="dialog" aria-modal="true" aria-labelledby="tour-title" aria-describedby="tour-text">' +
            '  <div class="tour-head">' +
            '    <span class="tour-level"></span>' +
            '    <button class="tour-exit" type="button">Salir <kbd>Esc</kbd></button>' +
            "  </div>" +
            '  <div class="tour-xp" aria-hidden="true"><div class="tour-xp-fill"></div></div>' +
            '  <div class="tour-body">' +
            '    <span class="tour-lumi">' + LUMI + "</span>" +
            '    <div class="tour-copy">' +
            '      <p class="tour-title" id="tour-title"></p>' +
            '      <p class="tour-text" id="tour-text"><span class="tour-typed" aria-hidden="true"></span><span class="tour-caret" aria-hidden="true"></span><span class="sr-only"></span></p>' +
            '      <p class="tour-badge" hidden>🏅 Logro desbloqueado: <strong>Explorador</strong></p>' +
            "    </div>" +
            "  </div>" +
            '  <div class="tour-actions">' +
            '    <button class="btn btn-small tour-back" type="button" aria-label="Paso anterior">◀</button>' +
            '    <a class="btn btn-secondary tour-go" href="/tutoria" hidden>Empezar tutoría</a>' +
            '    <button class="btn btn-primary tour-next" type="button"></button>' +
            "  </div>" +
            "</div>";
        document.body.appendChild(root);
        return {
            root: root,
            spotlight: root.querySelector(".tour-spotlight"),
            bubble: root.querySelector(".tour-bubble"),
            level: root.querySelector(".tour-level"),
            xp: root.querySelector(".tour-xp-fill"),
            title: root.querySelector(".tour-title"),
            typed: root.querySelector(".tour-typed"),
            caret: root.querySelector(".tour-caret"),
            spoken: root.querySelector(".tour-text .sr-only"),
            badge: root.querySelector(".tour-badge"),
            back: root.querySelector(".tour-back"),
            go: root.querySelector(".tour-go"),
            next: root.querySelector(".tour-next"),
        };
    }

    function targetOf(step) {
        return step.target ? document.querySelector('.nav .nav-link[href="' + step.target + '"]') : null;
    }

    // Ilumina el elemento del paso y pone la burbuja a su lado (o centrada si no hay elemento).
    function place() {
        const step = STEPS[index];
        const target = targetOf(step);
        const s = ui.spotlight;
        const b = ui.bubble;
        b.classList.toggle("is-docked", MOBILE.matches);

        if (!target) {
            // Sin elemento: el foco de luz se cierra en el centro y toda la pantalla queda oscura.
            s.style.left = window.innerWidth / 2 + "px";
            s.style.top = window.innerHeight / 2 + "px";
            s.style.width = "0px";
            s.style.height = "0px";
            b.style.left = "";
            b.style.top = "";
            b.classList.toggle("is-center", !MOBILE.matches);
            return;
        }
        const r = target.getBoundingClientRect();
        const pad = 6;
        s.style.left = r.left - pad + "px";
        s.style.top = r.top - pad + "px";
        s.style.width = r.width + pad * 2 + "px";
        s.style.height = r.height + pad * 2 + "px";

        b.classList.remove("is-center");
        if (MOBILE.matches) return; // en el celular la burbuja va abajo (CSS)
        const bh = b.offsetHeight;
        const top = Math.min(Math.max(r.top + r.height / 2 - bh / 2, 16), window.innerHeight - bh - 16);
        b.style.left = r.right + 24 + "px";
        b.style.top = top + "px";
    }

    function type(text) {
        window.clearInterval(typing);
        ui.spoken.textContent = text;
        if (QUIET.matches) {
            ui.typed.textContent = text;
            typing = null;
            return;
        }
        let i = 0;
        ui.typed.textContent = "";
        ui.caret.hidden = false;
        typing = window.setInterval(() => {
            i += 1;
            ui.typed.textContent = text.slice(0, i);
            if (i >= text.length) finishTyping();
        }, TYPE_MS);
    }

    function finishTyping() {
        window.clearInterval(typing);
        typing = null;
        ui.typed.textContent = STEPS[index].text;
        ui.caret.hidden = true;
    }

    function show(i) {
        index = i;
        const step = STEPS[index];
        const last = index === STEPS.length - 1;
        ui.level.textContent = "Nivel " + (index + 1) + "/" + STEPS.length;
        ui.xp.style.width = ((index + 1) / STEPS.length) * 100 + "%";
        ui.title.textContent = step.title;
        ui.badge.hidden = !step.final;
        ui.back.hidden = index === 0;
        ui.go.hidden = !last;
        ui.next.textContent = index === 0 ? "¡Vamos! ▶" : last ? "Terminar" : "Siguiente ▶";
        // La burbuja "salta" en cada paso, como en un juego.
        ui.bubble.classList.remove("is-hop");
        void ui.bubble.offsetWidth;
        ui.bubble.classList.add("is-hop");
        type(step.text);
        place();
        ui.next.focus();
    }

    function next() {
        // Primer toque: completa el texto. Segundo toque: avanza.
        if (typing) {
            finishTyping();
            return;
        }
        if (index === STEPS.length - 1) {
            close();
            return;
        }
        show(index + 1);
    }

    function back() {
        if (index > 0) show(index - 1);
    }

    function onKey(event) {
        if (event.key === "Escape") {
            event.preventDefault();
            close();
        } else if (event.key === "ArrowRight") {
            next();
        } else if (event.key === "ArrowLeft") {
            back();
        } else if (event.key === "Tab") {
            // El foco no sale de la burbuja mientras el tutorial está abierto.
            const items = Array.from(ui.bubble.querySelectorAll("button, a[href]")).filter((el) => !el.hidden);
            const first = items[0];
            const lastItem = items[items.length - 1];
            if (event.shiftKey && document.activeElement === first) {
                event.preventDefault();
                lastItem.focus();
            } else if (!event.shiftKey && document.activeElement === lastItem) {
                event.preventDefault();
                first.focus();
            }
        }
    }

    function setSidebar(open) {
        const sidebar = document.getElementById("sidebar");
        const scrim = document.getElementById("scrim");
        if (!sidebar) return;
        sidebar.classList.toggle("open", open);
        if (scrim) scrim.hidden = !open;
    }

    function open() {
        if (ui) return;
        ui = build();
        ui.root.querySelector(".tour-exit").addEventListener("click", close);
        ui.next.addEventListener("click", next);
        ui.back.addEventListener("click", back);
        document.addEventListener("keydown", onKey);
        window.addEventListener("resize", place);
        // En el celular el menú está escondido: se abre para que se vea lo que explica Lumi.
        openedSidebar = MOBILE.matches;
        if (openedSidebar) setSidebar(true);
        show(0);
    }

    function close() {
        if (!ui) return;
        window.clearInterval(typing);
        typing = null;
        document.removeEventListener("keydown", onKey);
        window.removeEventListener("resize", place);
        ui.root.remove();
        ui = null;
        if (openedSidebar) setSidebar(false);
        start.focus();
    }

    start.addEventListener("click", open);
})();
