// AI Job Copilot - Main Helper Script
document.addEventListener("DOMContentLoaded", function () {
  // Auto-dismiss alert messages after 5 seconds
  const alerts = document.querySelectorAll(".alert-dismissible");
  alerts.forEach(function (alert) {
    setTimeout(function () {
      try {
        const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
        bsAlert.close();
      } catch (e) {}
    }, 5000);
  });
});
