document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".comment-vote").forEach((button) => {
        button.addEventListener("click", () => {
            const direction = button.dataset.direction;
            button.classList.add("active");
            setTimeout(() => button.classList.remove("active"), 180);
            if (!button.dataset.notified) {
                const message = direction === "up"
                    ? "Voting is coming soon. Thanks for showing support!"
                    : "Downvotes will be available soon. We appreciate the feedback.";
                alert(message);
                button.dataset.notified = "true";
            }
        });
    });

    document.querySelectorAll(".comment-reply-button").forEach((button) => {
        const targetId = button.dataset.target;
        const form = document.getElementById(targetId);
        if (!form) {
            return;
        }
        button.addEventListener("click", () => {
            const isHidden = form.classList.toggle("hidden");
            button.classList.toggle("active", !isHidden);
            button.textContent = isHidden ? "Reply" : "Cancel";
        });
    });
});
