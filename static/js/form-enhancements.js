document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".file-upload input[type='file']").forEach((input) => {
        const wrapper = input.closest(".file-upload");
        if (!wrapper) {
            return;
        }
        const text = wrapper.querySelector(".file-upload-text");
        const placeholder = wrapper.dataset.placeholder || "Choose file";
        const preview = wrapper.parentElement.querySelector(".cover-preview");

        const setPreview = (file) => {
            if (!preview) {
                return;
            }
            if (file && file.type.startsWith("image/")) {
                const reader = new FileReader();
                reader.onload = (event) => {
                    let img = preview.querySelector("img");
                    if (!img) {
                        img = document.createElement("img");
                        preview.innerHTML = "";
                        preview.appendChild(img);
                    }
                    img.src = event.target.result;
                    preview.classList.add("show");
                };
                reader.readAsDataURL(file);
            } else if (preview.children.length) {
                preview.classList.add("show");
            } else {
                preview.classList.remove("show");
            }
        };

        if (preview && preview.children.length) {
            preview.classList.add("show");
        }

        input.addEventListener("change", () => {
            const file = input.files && input.files[0];
            if (file) {
                text.textContent = file.name;
            } else {
                text.textContent = placeholder;
            }
            setPreview(file);
        });
    });

    document.querySelectorAll("[data-password-confirm]").forEach((confirmField) => {
        const form = confirmField.form;
        if (!form) {
            return;
        }
        const primaryField = form.querySelector("[data-password-primary]");
        if (!primaryField) {
            return;
        }

        const wrapper = confirmField.closest(".password-toggle-wrapper") || confirmField;
        const message = document.createElement("div");
        message.className = "password-match-hint";
        const hintId = `${confirmField.id || confirmField.name || "password"}-hint-${Math.random()
            .toString(36)
            .slice(2, 7)}`;
        message.id = hintId;
        message.setAttribute("role", "status");
        message.setAttribute("aria-live", "polite");
        wrapper.insertAdjacentElement("afterend", message);
        confirmField.setAttribute("aria-describedby", hintId);

        const submitButton = form.querySelector("button[type='submit']");
        let confirmTouched = false;

        const setSubmitState = (disabled) => {
            if (!submitButton) {
                return;
            }
            submitButton.disabled = disabled;
        };

        const restartPulse = () => {
            message.classList.remove("pulse");
            void message.offsetWidth;
            message.classList.add("pulse");
        };

        const clearMessage = () => {
            message.textContent = "";
            message.classList.remove("is-visible", "is-match", "is-mismatch", "pulse");
            setSubmitState(false);
        };

        const showMessage = (text, state, disable = false) => {
            message.textContent = text;
            message.classList.add("is-visible");
            message.classList.remove("is-match", "is-mismatch");
            if (state === "match") {
                message.classList.add("is-match");
            }
            if (state === "mismatch") {
                message.classList.add("is-mismatch");
            }
            setSubmitState(disable);
            restartPulse();
        };

        const updateState = () => {
            const primaryValue = primaryField.value.trim();
            const confirmValue = confirmField.value.trim();

            if (!confirmTouched && !confirmValue) {
                clearMessage();
                return;
            }

            if (!confirmValue) {
                clearMessage();
                return;
            }

            if (!primaryValue) {
                showMessage("Enter your password above.", "mismatch", true);
                return;
            }

            if (primaryValue === confirmValue) {
                showMessage("Passwords match.", "match", false);
            } else {
                showMessage("Passwords do not match.", "mismatch", true);
            }
        };

        const markTouched = () => {
            confirmTouched = true;
            updateState();
        };

        confirmField.addEventListener("input", markTouched);
        confirmField.addEventListener("blur", markTouched);
        primaryField.addEventListener("input", updateState);

        updateState();
    });
});
