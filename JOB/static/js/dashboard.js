document.addEventListener("DOMContentLoaded", function () {
    // Application status select changer
    document.querySelectorAll(".select-app-status").forEach(select => {
        select.addEventListener("change", function () {
            const appId = this.getAttribute("data-app-id");
            const newStatus = this.value;

            fetch("/applications/api/update", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    application_id: appId,
                    status: newStatus
                })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    const badge = document.getElementById(`status-badge-${appId}`);
                    if (badge) {
                        badge.textContent = newStatus.charAt(0).toUpperCase() + newStatus.slice(1);
                    }
                }
            })
            .catch(err => console.error("Error updating status:", err));
        });
    });
});
