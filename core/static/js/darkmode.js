// Dark Mode Toggle
// Persists preference in localStorage so it survives page navigation

document.addEventListener("DOMContentLoaded", function () {
  const toggle = document.getElementById("darkModeToggle");
  const icon = toggle ? toggle.querySelector("i") : null;
  const brandSubtitle = document.querySelector(".brand-subtitle");

  function enableDark() {
    document.body.classList.add("dark-mode");
    if (icon) icon.classList.replace("bi-moon-fill", "bi-sun-fill");
    if (brandSubtitle) brandSubtitle.style.color = "rgba(255,255,255,0.65)";
  }

  function disableDark() {
    document.body.classList.remove("dark-mode");
    if (icon) icon.classList.replace("bi-sun-fill", "bi-moon-fill");
    if (brandSubtitle) brandSubtitle.style.color = "";
  }

  // Apply saved preference on load
  if (localStorage.getItem("darkMode") === "enabled") {
    enableDark();
  }

  if (toggle) {
    toggle.addEventListener("click", function () {
      if (document.body.classList.contains("dark-mode")) {
        disableDark();
        localStorage.setItem("darkMode", "disabled");
      } else {
        enableDark();
        localStorage.setItem("darkMode", "enabled");
      }
    });
  }
});
