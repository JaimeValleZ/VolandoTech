// Desplegables con diseño propio. El <select> original queda escondido debajo: el código de cada
// página sigue leyendo su valor y la validación "required" del formulario sigue funcionando.
(function () {
    const CHEVRON =
        '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" ' +
        'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 9l6 6 6-6"/></svg>';
    const CHECK =
        '<svg class="cselect-check" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" ' +
        'stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>';
    let counter = 0;

    function enhance(select) {
        const uid = "cselect-" + ++counter;
        const wrap = document.createElement("div");
        wrap.className = "cselect";
        select.parentNode.insertBefore(wrap, select);

        const button = document.createElement("button");
        button.type = "button";
        button.className = "cselect-button";
        button.id = uid + "-button";
        button.setAttribute("aria-haspopup", "listbox");
        button.setAttribute("aria-expanded", "false");
        button.innerHTML = '<span class="cselect-value" id="' + uid + '-value"></span><span class="cselect-chevron">' + CHEVRON + "</span>";

        const list = document.createElement("ul");
        list.className = "cselect-list";
        list.id = uid + "-list";
        list.setAttribute("role", "listbox");
        list.tabIndex = -1;
        list.hidden = true;
        button.setAttribute("aria-controls", list.id);

        // El botón va antes que el select: así, tocar el texto de la etiqueta abre el desplegable.
        wrap.append(button, select, list);
        select.classList.add("cselect-native");
        select.tabIndex = -1;
        select.setAttribute("aria-hidden", "true");

        // Nombre accesible: el texto de la etiqueta más el valor elegido.
        const caption = select.closest("label") && select.closest("label").querySelector("span");
        if (caption) {
            caption.id = caption.id || uid + "-label";
            button.setAttribute("aria-labelledby", caption.id + " " + uid + "-value");
            list.setAttribute("aria-labelledby", caption.id);
        }

        let active = -1;
        let typed = "";
        let typedTimer = null;

        function options() {
            return Array.from(list.children);
        }

        function render() {
            list.replaceChildren();
            Array.from(select.options).forEach((opt, i) => {
                const item = document.createElement("li");
                item.id = uid + "-opt-" + i;
                item.className = "cselect-option";
                item.setAttribute("role", "option");
                item.setAttribute("aria-selected", String(i === select.selectedIndex));
                item.innerHTML = CHECK;
                const text = document.createElement("span");
                text.textContent = opt.textContent;
                item.prepend(text);
                if (opt.disabled) item.setAttribute("aria-disabled", "true");
                list.appendChild(item);
            });
            const current = select.options[select.selectedIndex];
            button.querySelector(".cselect-value").textContent = current ? current.textContent : "Elige una opción";
            button.disabled = select.disabled || select.options.length === 0;
        }

        function setActive(i) {
            const items = options();
            if (!items.length) return;
            active = Math.max(0, Math.min(i, items.length - 1));
            items.forEach((el, n) => el.classList.toggle("is-active", n === active));
            list.setAttribute("aria-activedescendant", items[active].id);
            items[active].scrollIntoView({ block: "nearest" });
        }

        function open() {
            if (button.disabled || !list.hidden) return;
            list.hidden = false;
            wrap.classList.add("is-open");
            button.setAttribute("aria-expanded", "true");
            // Si no cabe abajo, se abre hacia arriba.
            const room = window.innerHeight - button.getBoundingClientRect().bottom;
            wrap.classList.toggle("is-up", room < Math.min(list.scrollHeight, 320) + 16);
            setActive(Math.max(select.selectedIndex, 0));
            list.focus();
        }

        function close(focusButton) {
            if (list.hidden) return;
            list.hidden = true;
            wrap.classList.remove("is-open", "is-up");
            button.setAttribute("aria-expanded", "false");
            if (focusButton) button.focus();
        }

        function choose(i) {
            if (i < 0 || select.options[i].disabled) return;
            if (select.selectedIndex !== i) {
                select.selectedIndex = i;
                select.dispatchEvent(new Event("change", { bubbles: true }));
            }
            render();
            close(true);
        }

        // Escribir una letra salta a la primera opción que empieza así (por ejemplo, "8" en la edad).
        function typeAhead(key) {
            window.clearTimeout(typedTimer);
            typed += key.toLowerCase();
            typedTimer = window.setTimeout(() => (typed = ""), 600);
            const match = options().findIndex((el) => el.textContent.trim().toLowerCase().startsWith(typed));
            if (match >= 0) setActive(match);
        }

        button.addEventListener("click", () => (list.hidden ? open() : close(true)));
        button.addEventListener("keydown", (event) => {
            if (["ArrowDown", "ArrowUp", "Enter", " "].includes(event.key)) {
                event.preventDefault();
                open();
            }
        });

        list.addEventListener("keydown", (event) => {
            const last = options().length - 1;
            if (event.key === "ArrowDown") setActive(active + 1);
            else if (event.key === "ArrowUp") setActive(active - 1);
            else if (event.key === "Home") setActive(0);
            else if (event.key === "End") setActive(last);
            else if (event.key === "Enter" || event.key === " ") choose(active);
            else if (event.key === "Escape") {
                event.stopPropagation();
                close(true);
            } else if (event.key === "Tab") {
                close(false);
                return;
            } else if (event.key.length === 1) typeAhead(event.key);
            else return;
            event.preventDefault();
        });

        list.addEventListener("click", (event) => {
            const item = event.target.closest(".cselect-option");
            if (item) choose(options().indexOf(item));
        });
        list.addEventListener("mousemove", (event) => {
            const item = event.target.closest(".cselect-option");
            if (item) setActive(options().indexOf(item));
        });

        document.addEventListener("pointerdown", (event) => {
            if (!wrap.contains(event.target)) close(false);
        });

        // Las opciones pueden llegar después (los libros se cargan de la base): se vuelve a dibujar.
        new MutationObserver(render).observe(select, { childList: true, subtree: true, characterData: true, attributes: true });
        select.addEventListener("change", render);
        render();
    }

    document.querySelectorAll("select:not([multiple])").forEach(enhance);
})();
