document.addEventListener("DOMContentLoaded", function () {
    // Bookmark Toggle Handler
    document.querySelectorAll(".btn-save-job").forEach(button => {
        button.addEventListener("click", function (e) {
            e.preventDefault();
            const jobId = this.getAttribute("data-job-id");
            if (!jobId) return;

            fetch(`/api/jobs/save/${jobId}`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                }
            })
            .then(res => res.json())
            .then(data => {
                if (data.saved) {
                    this.classList.remove("btn-outline-secondary");
                    this.classList.add("btn-warning", "text-dark");
                    this.innerHTML = '<i class="bi bi-bookmark-fill me-1"></i> Saved';
                } else {
                    this.classList.remove("btn-warning", "text-dark");
                    this.classList.add("btn-outline-secondary");
                    this.innerHTML = '<i class="bi bi-bookmark me-1"></i> Save';
                }
            })
            .catch(err => console.error("Error saving job:", err));
        });
    });
});
