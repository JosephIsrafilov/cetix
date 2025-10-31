document.addEventListener("DOMContentLoaded", () => {
    const confirmModal = document.getElementById("confirm-modal");
    const confirmMessage = confirmModal ? document.getElementById("confirm-modal-message") : null;
    const confirmAccept = confirmModal ? confirmModal.querySelector(".confirm-modal-confirm") : null;
    const confirmCancel = confirmModal ? confirmModal.querySelector(".confirm-modal-cancel") : null;
    const confirmClose = confirmModal ? confirmModal.querySelector(".confirm-modal-close") : null;

    let pendingForm = null;
    let previousFocus = null;

    const closeModal = () => {
        if (!confirmModal) {
            return;
        }
        confirmModal.classList.remove("active");
        confirmModal.classList.add("hidden");
        document.body.classList.remove("modal-open");
        if (previousFocus) {
            previousFocus.focus();
            previousFocus = null;
        }
        pendingForm = null;
    };

    const openModal = (message, confirmLabel) => {
        if (!confirmModal || !confirmAccept || !confirmMessage) {
            return true;
        }
        confirmMessage.textContent = message || "Are you sure?";
        const defaultLabel = confirmAccept.dataset.defaultLabel || confirmAccept.textContent;
        confirmAccept.textContent = confirmLabel || defaultLabel;
        previousFocus = document.activeElement;
        confirmModal.classList.remove("hidden");
        confirmModal.classList.add("active");
        document.body.classList.add("modal-open");
        window.setTimeout(() => confirmAccept.focus(), 10);
        return false;
    };

    if (confirmAccept) {
        confirmAccept.dataset.defaultLabel = confirmAccept.textContent;
        confirmAccept.addEventListener("click", () => {
            if (pendingForm) {
                const form = pendingForm;
                pendingForm = null;
                form.dataset.skipConfirm = "true";
                if (typeof form.requestSubmit === "function") {
                    form.requestSubmit();
                } else {
                    form.submit();
                }
            }
            closeModal();
        });
    }

    const cancelButtons = [confirmCancel, confirmClose];
    cancelButtons.forEach((button) => {
        if (!button) {
            return;
        }
        button.addEventListener("click", () => {
            closeModal();
        });
    });

    if (confirmModal) {
        confirmModal.addEventListener("click", (event) => {
            if (event.target === confirmModal) {
                closeModal();
            }
        });
    }

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape" && confirmModal && !confirmModal.classList.contains("hidden")) {
            event.preventDefault();
            closeModal();
        }
    });

    document.querySelectorAll(".comment-vote").forEach((button) => {
        button.addEventListener("click", () => {
            button.classList.add("active");
            window.setTimeout(() => button.classList.remove("active"), 180);
            if (!button.dataset.notified) {
                button.dataset.notified = "true";
            }
        });
    });

    document.querySelectorAll(".comment-reply-button").forEach((button) => {
        const targetId = button.dataset.target;
        const form = document.getElementById(targetId);
        const label = button.querySelector(".label");
        const icon = button.querySelector(".icon");
        if (!form || !label) {
            return;
        }
        const defaultLabel = label.textContent.trim() || "Reply";
        const cancelLabel = button.dataset.cancelLabel || "Cancel";
        const defaultIcon = icon ? icon.textContent.trim() || "?" : "?";
        const cancelIcon = "?";

        button.addEventListener("click", () => {
            const isHidden = form.classList.toggle("hidden");
            button.classList.toggle("active", !isHidden);
            label.textContent = isHidden ? defaultLabel : cancelLabel;
            if (icon) {
                icon.textContent = isHidden ? defaultIcon : cancelIcon;
            }
        });
    });

    document.querySelectorAll(".comment-delete-form").forEach((form) => {
        form.addEventListener("submit", (event) => {
            if (form.dataset.skipConfirm === "true") {
                form.dataset.skipConfirm = "false";
                return;
            }
            event.preventDefault();
            const message = form.dataset.confirm || "Delete this comment?";
            const confirmLabel = form.dataset.confirmLabel || "Delete";
            const handledByModal = openModal(message, confirmLabel);
            if (handledByModal === false) {
                pendingForm = form;
            } else if (window.confirm(message)) {
                form.dataset.skipConfirm = "true";
                form.submit();
            }
        });
    });
});
