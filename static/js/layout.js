document.addEventListener("DOMContentLoaded", () => {
    const profileToggle = document.querySelector(".profile-toggle");
    const profileDropdown = document.querySelector(".profile-dropdown");

    if (profileToggle && profileDropdown) {
        profileToggle.addEventListener("click", (event) => {
            event.stopPropagation();
            profileDropdown.classList.toggle("open");
            profileDropdown.classList.toggle("hidden");
            const expanded = profileDropdown.classList.contains("open");
            profileToggle.setAttribute("aria-expanded", expanded ? "true" : "false");
        });

        document.addEventListener("click", (event) => {
            if (!profileDropdown.contains(event.target) && event.target !== profileToggle) {
                profileDropdown.classList.add("hidden");
                profileDropdown.classList.remove("open");
                profileToggle.setAttribute("aria-expanded", "false");
            }
        });

        document.addEventListener("keydown", (event) => {
            if (event.key === "Escape") {
                profileDropdown.classList.add("hidden");
                profileDropdown.classList.remove("open");
                profileToggle.setAttribute("aria-expanded", "false");
                profileToggle.focus();
            }
        });
    }
});
