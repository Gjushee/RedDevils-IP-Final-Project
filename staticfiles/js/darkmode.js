// Dark Mode Toggle
// Persists preference in localStorage so it survives page navigation
 
document.addEventListener("DOMContentLoaded", function () {
  const toggle = document.getElementById("darkModeToggle");
  const icon = toggle ? toggle.querySelector("i") : null;
 
  // Apply saved preference on load
  if (localStorage.getItem("darkMode") === "enabled") {
    document.body.classList.add("dark-mode");
    if (icon) {
      icon.classList.replace("bi-moon-fill", "bi-sun-fill");
    }
  }
 
  if (toggle) {
    toggle.addEventListener("click", function () {
      document.body.classList.toggle("dark-mode");
 
      if (document.body.classList.contains("dark-mode")) {
        localStorage.setItem("darkMode", "enabled");
        if (icon) icon.classList.replace("bi-moon-fill", "bi-sun-fill");
      } else {
        localStorage.setItem("darkMode", "disabled");
        if (icon) icon.classList.replace("bi-sun-fill", "bi-moon-fill");
      }
    });
  }
});