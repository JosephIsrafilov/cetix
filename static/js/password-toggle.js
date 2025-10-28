document.addEventListener("DOMContentLoaded", () => {
    const iconShow = `
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <path d="M12 5C7 5 2.73 8.11 1 12c1.73 3.89 6 7 11 7s9.27-3.11 11-7c-1.73-3.89-6-7-11-7Z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            <circle cx="12" cy="12" r="3.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>`;

    const iconHide = `
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <path d="M3 3l18 18" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            <path d="M9.88 5.088A10.225 10.225 0 0 1 12 5c5 0 9.27 3.11 11 7-.61 1.38-1.56 2.64-2.75 3.69M6.63 6.63C4.37 8.12 2.75 9.97 2 12c1.73 3.89 6 7 11 7 1.18 0 2.31-.16 3.36-.45" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M9.88 12.04c-.01.08-.02.16-.02.24a2.15 2.15 0 0 0 3.7 1.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>`;

    function attachToggle(input, button) {
        if (!input || !button || button.dataset.toggleReady === "true") {
            return;
        }
        button.dataset.toggleReady = "true";
        button.innerHTML = iconShow;
        button.setAttribute("aria-label", "Show password");

        button.addEventListener("click", () => {
            const isHidden = input.getAttribute("type") === "password";
            input.setAttribute("type", isHidden ? "text" : "password");
            button.setAttribute("aria-label", isHidden ? "Hide password" : "Show password");
            button.classList.toggle("password-visible", isHidden);
            button.innerHTML = isHidden ? iconHide : iconShow;
        });
    }

    function createWrapper(input) {
        if (input.closest(".password-toggle-wrapper")) {
            const existingButton = input.closest(".password-toggle-wrapper").querySelector(".password-toggle");
            if (existingButton) {
                attachToggle(input, existingButton);
                return;
            }
        }
        const wrapper = document.createElement("div");
        wrapper.className = "password-toggle-wrapper";
        input.parentNode.insertBefore(wrapper, input);
        wrapper.appendChild(input);

        const control = document.createElement("button");
        control.type = "button";
        control.className = "password-toggle";
        wrapper.appendChild(control);

        attachToggle(input, control);
    }

    document.querySelectorAll(".password-toggle-wrapper").forEach((wrapper) => {
        const input = wrapper.querySelector('input[type="password"]');
        const button = wrapper.querySelector(".password-toggle");
        if (input) {
            if (!button) {
                const control = document.createElement("button");
                control.type = "button";
                control.className = "password-toggle";
                wrapper.appendChild(control);
                attachToggle(input, control);
            } else {
                attachToggle(input, button);
            }
        }
    });

    document.querySelectorAll('input[type="password"]').forEach((input) => {
        createWrapper(input);
    });
});
