// Module preload polyfill for browsers that don't support it
import "vite/modulepreload-polyfill";

// Main JavaScript entry point
import "../css/input.css"; // Updated path

// Hot module replacement for development
if (import.meta.hot) {
  import.meta.hot.accept();
}

// Add any JavaScript functionality here
console.log("Vite + Django + Tailwind CSS loaded!");

// Example: Add interactive functionality
document.addEventListener("DOMContentLoaded", function () {
  // Mobile menu toggle
  const mobileMenuButton = document.querySelector("[data-mobile-menu-button]");
  const mobileMenu = document.querySelector("[data-mobile-menu]");

  if (mobileMenuButton && mobileMenu) {
    mobileMenuButton.addEventListener("click", function () {
      mobileMenu.classList.toggle("hidden");
    });
  }

  // Add any other interactive features here
});
