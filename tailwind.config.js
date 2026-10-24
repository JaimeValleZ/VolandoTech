/** @type {import('tailwindcss').Config} */
module.exports = {
    content: ["./templates/**/*.html", "./static/js/**/*.js"],
    // Sin el reinicio global de Tailwind: los estilos de styles.css siguen mandando
    // y Tailwind solo agrega las clases que se usan en las plantillas.
    corePlugins: { preflight: false },
    // Las variantes dark: se activan con el tema elegido en la app, no solo con el del sistema.
    darkMode: ["selector", '[data-theme="dark"]'],
    theme: {
        extend: {
            // Los colores salen de las variables de styles.css, así cambian solos en modo oscuro.
            colors: {
                mint: {
                    50: "var(--mint-50)",
                    100: "var(--mint-100)",
                    200: "var(--mint-200)",
                    300: "var(--mint-300)",
                    400: "var(--mint-400)",
                    500: "var(--mint-500)",
                    700: "var(--mint-700)",
                    900: "var(--mint-900)",
                },
                ink: { DEFAULT: "var(--ink)", soft: "var(--ink-soft)" },
                surface: "var(--surface)",
            },
            keyframes: {
                // Aplasta, rebota un poco más grande y vuelve: el "plop" de los botones.
                plop: {
                    "0%": { transform: "scale(1)" },
                    "30%": { transform: "scale(0.9)" },
                    "60%": { transform: "scale(1.06)" },
                    "80%": { transform: "scale(0.98)" },
                    "100%": { transform: "scale(1)" },
                },
                "pop-in": {
                    "0%": { opacity: "0", transform: "scale(0.85)" },
                    "70%": { opacity: "1", transform: "scale(1.03)" },
                    "100%": { opacity: "1", transform: "scale(1)" },
                },
                nudge: {
                    "0%, 100%": { transform: "translateY(0)" },
                    "50%": { transform: "translateY(-6px)" },
                },
            },
            animation: {
                plop: "plop 0.38s ease-out",
                "pop-in": "pop-in 0.35s ease-out both",
                nudge: "nudge 0.9s ease-in-out infinite",
            },
        },
    },
};
