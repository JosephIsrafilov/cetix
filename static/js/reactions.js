function ready(fn) {
    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", fn);
    } else {
        fn();
    }
}

ready(() => {
    const reactionForms = document.querySelectorAll(".reaction-form");
    const STORAGE_PREFIX = "article-stats-";

    applyStoredStats();
    window.addEventListener("pageshow", applyStoredStats);

    reactionForms.forEach((form) => {
        const handleSubmit = (event) => {
            event.preventDefault();
            const submitButton = form.querySelector("button");
            if (submitButton) {
                submitButton.disabled = true;
            }

            const formData = new FormData(form);
            fetch(form.action, {
                method: "POST",
                body: formData,
                credentials: "same-origin",
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                    Accept: "application/json",
                },
            })
                .then((response) => {
                    if (!response.ok) {
                        throw new Error("Failed to toggle reaction.");
                    }
                    return response.json();
                })
                .then((data) => {
                    persistStats(form.dataset.article, data);
                    updateReactionButtons(form.dataset.article, data.reaction);
                    updateReactionStats(form.dataset.article, data);
                })
                .catch(() => {
                    form.removeEventListener("submit", handleSubmit);
                    form.submit();
                })
                .finally(() => {
                    if (submitButton) {
                        submitButton.disabled = false;
                    }
                });
        };

        form.addEventListener("submit", handleSubmit);
    });

    function applyStoredStats() {
        document.querySelectorAll("[data-article-card]").forEach((card) => {
            const slug = card.dataset.articleCard;
            if (!slug) {
                return;
            }
            const stored = readStats(slug);
            if (stored) {
                syncArticleCards(slug, stored);
                updateReactionButtons(slug, stored.reaction || null);
            }
        });

        document.querySelectorAll("[data-article-stats]").forEach((statsEl) => {
            const slug = statsEl.dataset.articleStats;
            if (!slug) {
                return;
            }
            const stored = readStats(slug);
            if (stored) {
                syncArticleCards(slug, stored);
            }
        });
    }

    function persistStats(slug, data) {
        const payload = {
            score: data.score,
            likes: data.likes,
            dislikes: data.dislikes,
            reaction: data.reaction,
        };
        try {
            sessionStorage.setItem(
                `${STORAGE_PREFIX}${slug}`,
                JSON.stringify(payload)
            );
        } catch (error) {
            // Ignore storage failures (quota, disabled, etc.).
        }
        syncArticleCards(slug, payload);
    }

    function readStats(slug) {
        try {
            const raw = sessionStorage.getItem(`${STORAGE_PREFIX}${slug}`);
            if (!raw) {
                return null;
            }
            return JSON.parse(raw);
        } catch (error) {
            return null;
        }
    }

    function updateReactionButtons(slug, activeReaction) {
        document
            .querySelectorAll(`.reaction-form[data-article="${slug}"]`)
            .forEach((otherForm) => {
                const button = otherForm.querySelector("button");
                if (!button) {
                    return;
                }
                const reactionValue = otherForm.dataset.reaction;
                button.classList.toggle("active", activeReaction === reactionValue);
            });
    }

    function updateReactionStats(slug, data) {
        const container = document.querySelector(
            `[data-article-stats="${slug}"]`
        );
        if (!container) {
            return;
        }
        const map = {
            score: data.score,
            likes: data.likes,
            dislikes: data.dislikes,
        };
        Object.entries(map).forEach(([key, value]) => {
            const chip = container.querySelector(`[data-stat="${key}"] strong`);
            if (chip && typeof value === "number") {
                chip.textContent = value;
            }
        });
    }

    function syncArticleCards(slug, data) {
        const selectors = [
            `[data-article-card="${slug}"] [data-article-stats="${slug}"]`,
            `[data-article-stats="${slug}"]`,
        ];
        selectors.forEach((selector) => {
            document.querySelectorAll(selector).forEach((statsContainer) => {
                const map = {
                    score: data.score,
                    likes: data.likes,
                    dislikes: data.dislikes,
                };
                Object.entries(map).forEach(([key, value]) => {
                    const chip = statsContainer.querySelector(
                        `[data-stat="${key}"] strong`
                    );
                    if (chip && typeof value === "number") {
                        chip.textContent = value;
                    }
                });
            });
        });
    }
});
