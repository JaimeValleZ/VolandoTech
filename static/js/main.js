// Lee un texto en voz alta con la voz de Microsoft Edge que genera el servidor (es-CO-SalomeNeural).
let audioActual = null;
let pedidoVoz = 0;

window.leerEnVoz = async function (texto) {
    if (audioActual) audioActual.pause();
    // Si el niño toca otro botón mientras llega el audio, solo suena el último.
    const pedido = ++pedidoVoz;
    try {
        const res = await fetch("/api/voz", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text: texto.slice(0, 4000) }),
        });
        if (!res.ok) throw new Error("voz no disponible");
        const { url } = await res.json();
        if (pedido !== pedidoVoz) return true;
        // El audio empieza a sonar mientras el servidor lo sigue generando.
        const audio = new Audio(url);
        audioActual = audio;
        await audio.play();
        return true;
    } catch (error) {
        return false;
    }
};

// Efecto plop: el elemento se aplasta y rebota al tocarlo (la animación está en tailwind.src.css).
(function () {
    const INTERACTIVOS = "button, .btn, .nav-link, .part-btn, .feature-card, [data-drop-zone], summary";

    document.addEventListener("click", (event) => {
        const el = event.target.closest(INTERACTIVOS);
        if (!el || el.disabled) return;
        el.classList.remove("plop");
        void el.offsetWidth; // reinicia la animación si se toca varias veces seguidas
        el.classList.add("plop");
    });
    document.addEventListener("animationend", (event) => {
        if (event.animationName === "plop") event.target.classList.remove("plop");
    });
})();

// Modo claro / oscuro. Empieza en claro; el script del <head> (base.html) aplica la elección guardada antes de pintar.
(function () {
    const button = document.getElementById("theme-toggle");
    if (!button) return;
    const root = document.documentElement;
    const label = button.querySelector(".nav-label");
    function aplicar(tema, animar) {
        if (animar) {
            root.classList.add("theme-changing");
            window.setTimeout(() => root.classList.remove("theme-changing"), 350);
        }
        root.setAttribute("data-theme", tema);
        const oscuro = tema === "dark";
        // El botón dice a qué modo se pasa al tocarlo.
        const texto = oscuro ? "Modo claro" : "Modo oscuro";
        label.textContent = texto;
        button.dataset.label = texto;
        button.setAttribute("aria-pressed", String(oscuro));
    }

    button.addEventListener("click", () => {
        const tema = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
        try {
            localStorage.setItem("tema", tema);
        } catch (e) {}
        aplicar(tema, true);
    });

    aplicar(root.getAttribute("data-theme") || "light", false);
})();

// Esconder la barra lateral y dejar solo los iconos (pantallas grandes). Se recuerda entre páginas.
(function () {
    const toggle = document.getElementById("sidebar-toggle");
    if (!toggle) return;
    const root = document.documentElement;
    const label = toggle.querySelector(".nav-label");

    function sync() {
        const collapsed = root.classList.contains("sidebar-collapsed");
        toggle.setAttribute("aria-expanded", String(!collapsed));
        label.textContent = collapsed ? "Mostrar menú" : "Ocultar menú";
    }

    toggle.addEventListener("click", () => {
        const collapsed = root.classList.toggle("sidebar-collapsed");
        try {
            localStorage.setItem("sidebarCollapsed", collapsed ? "1" : "0");
        } catch (e) {}
        sync();
    });
    sync();
})();

// Términos y condiciones: hay que aceptarlos para usar la app. Se recuerda en este navegador.
(function () {
    const dialog = document.getElementById("terms");
    if (!dialog || typeof dialog.showModal !== "function") return;
    // Cambia esta versión si los términos cambian: todos tendrán que aceptarlos de nuevo.
    const VERSION = "2026-10-23";
    const KEY = "terminosAceptados";
    const ask = document.getElementById("terms-ask");
    const rejected = document.getElementById("terms-rejected");

    function accepted() {
        try {
            return localStorage.getItem(KEY) === VERSION;
        } catch (e) {
            return false;
        }
    }

    function showStep(step) {
        ask.hidden = step !== ask;
        rejected.hidden = step !== rejected;
        // El foco va al enlace de los términos y no a "Acepto", para no aceptar con un Enter sin leer.
        (step.querySelector(".terms-link") || step.querySelector(".btn-primary")).focus();
    }

    if (accepted()) return;

    // Escape no cierra la ventana: hay que elegir una opción.
    dialog.addEventListener("cancel", (event) => event.preventDefault());

    document.getElementById("terms-accept").addEventListener("click", () => {
        try {
            localStorage.setItem(KEY, VERSION);
        } catch (e) {}
        dialog.close();
    });
    document.getElementById("terms-reject").addEventListener("click", () => showStep(rejected));
    document.getElementById("terms-review").addEventListener("click", () => showStep(ask));

    dialog.showModal();
    showStep(ask);
})();

// Botón fijo para volver arriba: está siempre a la vista en las páginas que tienen scroll.
(function () {
    const button = document.getElementById("to-top");
    if (!button) return;
    let pendiente = false;

    function update() {
        pendiente = false;
        // Solo se esconde si todo el contenido cabe en la pantalla.
        button.hidden = document.documentElement.scrollHeight <= window.innerHeight + 1;
    }

    function schedule() {
        if (!pendiente) {
            pendiente = true;
            requestAnimationFrame(update);
        }
    }

    window.addEventListener("resize", schedule);
    // El contenido crece sin hacer scroll (un cuento que llega, una parte del libro): se vuelve a medir.
    if ("ResizeObserver" in window) new ResizeObserver(schedule).observe(document.body);
    schedule();

    button.addEventListener("click", () => {
        const suave = !window.matchMedia("(prefers-reduced-motion: reduce)").matches;
        window.scrollTo({ top: 0, behavior: suave ? "smooth" : "auto" });
        // El foco vuelve al inicio del contenido, para quien navega con teclado.
        const main = document.querySelector(".content");
        if (main) {
            main.setAttribute("tabindex", "-1");
            main.focus({ preventScroll: true });
        }
    });
})();

// Barra lateral deslizante en pantallas pequeñas
(function () {
    const sidebar = document.getElementById("sidebar");
    const scrim = document.getElementById("scrim");
    const button = document.getElementById("menu-btn");
    if (!sidebar || !scrim || !button) return;

    function setOpen(open) {
        sidebar.classList.toggle("open", open);
        scrim.hidden = !open;
        button.setAttribute("aria-expanded", String(open));
    }

    button.addEventListener("click", () => setOpen(!sidebar.classList.contains("open")));
    scrim.addEventListener("click", () => setOpen(false));
    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape") setOpen(false);
    });
    sidebar.querySelectorAll("a").forEach((link) => link.addEventListener("click", () => setOpen(false)));
})();
