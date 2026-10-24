// Zona para subir archivos (templates/_upload.html): arrastrar y soltar, e icono según el tipo.
(function () {
    const TYPES = {
        pdf: { label: "PDF", color: "#d64045", exts: ["pdf"] },
        image: { label: "IMG", color: "#2f9e6a", exts: ["jpg", "jpeg", "png", "webp", "bmp", "tiff", "tif"] },
        word: { label: "DOC", color: "#2b6cb0", exts: ["docx"] },
        slides: { label: "PPT", color: "#dd6b20", exts: ["pptx"] },
        text: { label: "TXT", color: "#5f6368", exts: ["txt", "md"] },
    };
    const DRAG_CLASSES = ["border-mint-500", "bg-mint-100", "scale-[1.02]"];

    function typeOf(name) {
        const ext = name.split(".").pop().toLowerCase();
        return Object.values(TYPES).find((t) => t.exts.includes(ext)) || TYPES.text;
    }

    // Hoja con la esquina doblada y una etiqueta de color con el tipo de archivo.
    function iconSvg(type) {
        const body = type === TYPES.image
            ? '<circle cx="17" cy="18" r="3" fill="' + type.color + '" opacity="0.35"/>' +
              '<path d="M10 31l7-7 5 5 4-4 8 6" stroke="' + type.color + '" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" opacity="0.6"/>'
            : '<path d="M12 16h14M12 22h18M12 28h12" stroke="' + type.color + '" stroke-width="2.4" stroke-linecap="round" opacity="0.35"/>';
        return (
            '<svg width="44" height="52" viewBox="0 0 44 52" fill="none" aria-hidden="true">' +
            '<path d="M6 2h22l12 12v32a4 4 0 0 1-4 4H6a4 4 0 0 1-4-4V6a4 4 0 0 1 4-4z" fill="#fff" stroke="' + type.color + '" stroke-width="2.5"/>' +
            '<path d="M28 2v8a4 4 0 0 0 4 4h8" stroke="' + type.color + '" stroke-width="2.5" stroke-linejoin="round"/>' +
            body +
            '<rect x="6" y="36" width="26" height="11" rx="5.5" fill="' + type.color + '"/>' +
            '<text x="19" y="44.5" text-anchor="middle" font-family="system-ui, sans-serif" font-size="8" font-weight="700" fill="#fff">' + type.label + "</text>" +
            "</svg>"
        );
    }

    function formatSize(bytes) {
        if (bytes < 1024) return bytes + " B";
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(0) + " KB";
        return (bytes / (1024 * 1024)).toFixed(1) + " MB";
    }

    document.querySelectorAll("[data-file-drop]").forEach((root) => {
        const input = root.querySelector('input[type="file"]');
        const zone = root.querySelector("[data-drop-zone]");
        const chosen = root.querySelector("[data-file-chosen]");

        function render() {
            const file = input.files[0];
            chosen.hidden = !file;
            if (!file) return;
            root.querySelector("[data-file-icon]").innerHTML = iconSvg(typeOf(file.name));
            root.querySelector("[data-file-name]").textContent = file.name;
            root.querySelector("[data-file-size]").textContent = formatSize(file.size);
            // Reinicia la animación de entrada si se elige otro archivo.
            chosen.classList.remove("animate-pop-in");
            void chosen.offsetWidth;
            chosen.classList.add("animate-pop-in");
        }

        input.addEventListener("change", render);

        root.querySelector("[data-file-clear]").addEventListener("click", () => {
            input.value = "";
            render();
            input.focus();
        });

        ["dragenter", "dragover"].forEach((name) =>
            zone.addEventListener(name, (event) => {
                event.preventDefault();
                zone.classList.add(...DRAG_CLASSES);
            })
        );
        zone.addEventListener("dragleave", (event) => {
            // Pasar sobre el dibujo o los textos de la zona no cuenta como salir.
            if (!zone.contains(event.relatedTarget)) zone.classList.remove(...DRAG_CLASSES);
        });
        zone.addEventListener("drop", (event) => {
            event.preventDefault();
            zone.classList.remove(...DRAG_CLASSES);
            if (!event.dataTransfer.files.length) return;
            input.files = event.dataTransfer.files;
            input.dispatchEvent(new Event("change"));
        });
    });
})();
