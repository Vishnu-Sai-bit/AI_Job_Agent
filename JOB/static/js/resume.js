document.addEventListener("DOMContentLoaded", function () {
    const dropzone = document.getElementById("resume-dropzone");
    const fileInput = document.getElementById("resume-file-input");
    const fileNameDisplay = document.getElementById("selected-file-name");
    const submitBtn = document.getElementById("btn-submit-resume");

    if (dropzone && fileInput) {
        dropzone.addEventListener("click", () => fileInput.click());

        ["dragenter", "dragover"].forEach(eventName => {
            dropzone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropzone.classList.add("dragover");
            }, false);
        });

        ["dragleave", "drop"].forEach(eventName => {
            dropzone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropzone.classList.remove("dragover");
            }, false);
        });

        dropzone.addEventListener("drop", (e) => {
            const dt = e.dataTransfer;
            const files = dt.files;
            if (files.length > 0) {
                fileInput.files = files;
                updateFileInfo(files[0]);
            }
        });

        fileInput.addEventListener("change", function () {
            if (this.files.length > 0) {
                updateFileInfo(this.files[0]);
            }
        });
    }

    function updateFileInfo(file) {
        if (!fileNameDisplay) return;
        const sizeMb = (file.size / (1024 * 1024)).toFixed(2);
        fileNameDisplay.innerHTML = `<strong>Selected:</strong> ${file.name} (${sizeMb} MB)`;
        if (submitBtn) {
            submitBtn.removeAttribute("disabled");
        }
    }
});
