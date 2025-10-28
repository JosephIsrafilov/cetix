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
});
