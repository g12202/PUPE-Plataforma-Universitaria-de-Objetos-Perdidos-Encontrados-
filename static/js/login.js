
document.addEventListener("DOMContentLoaded", () => {
    const card = document.querySelector(".login-card");
    const inputs = document.querySelectorAll(".neu-input input");
    const toggle = document.getElementById("passwordToggle");
    const password = document.getElementById("password");
    const form = document.querySelector(".login-form");
    const submitButton = form?.querySelector(".login-btn");

    // Efecto de relieve en el icono.
    document.querySelectorAll(".neu-icon, .neu-toggle").forEach((element) => {
        element.addEventListener("mouseenter", () => {
            element.style.transform = "scale(1.05)";
        });

        element.addEventListener("mouseleave", () => {
            element.style.transform = "";
        });
    });

    // Luz ambiental que sigue el cursor.
    if (card && window.matchMedia("(pointer: fine)").matches) {
        card.addEventListener("mousemove", (event) => {
            const rect = card.getBoundingClientRect();

            const x = (event.clientX - rect.left) / rect.width - 0.5;
            const y = (event.clientY - rect.top) / rect.height - 0.5;

            card.style.boxShadow = `
                ${x * 24}px ${y * 24}px 60px #bec3cf,
                ${-x * 24}px ${-y * 24}px 60px #ffffff
            `;
        });

        card.addEventListener("mouseleave", () => {
            card.style.boxShadow = "";
        });
    }

    // Efecto al enfocar y abandonar los campos.
    inputs.forEach((input) => {
        input.addEventListener("focus", () => {
            input.closest(".neu-input").style.transform = "scale(0.99)";
        });

        input.addEventListener("blur", () => {
            input.closest(".neu-input").style.transform = "";
        });
    });

    // Mostrar u ocultar contraseña.
    if (toggle && password) {
        toggle.addEventListener("click", () => {
            const showing = password.type === "password";

            password.type = showing ? "text" : "password";
            toggle.classList.toggle("show-password", showing);
            toggle.setAttribute(
                "aria-pressed",
                String(showing)
            );
            toggle.setAttribute(
                "aria-label",
                showing ? "Ocultar contraseña" : "Mostrar contraseña"
            );

            password.focus();
        });
    }

    // Indicar que se está enviando el formulario.
    // Django se encarga de comprobar las credenciales.
    if (form && submitButton) {
        form.addEventListener("submit", () => {
            if (!form.checkValidity()) {
                return;
            }

            submitButton.classList.add("loading");
            submitButton.setAttribute("aria-busy", "true");
            submitButton.disabled = true;
        });
    }
});
