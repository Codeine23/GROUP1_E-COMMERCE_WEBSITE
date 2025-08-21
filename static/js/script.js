const hamburger = document.getElementById("hamburger");
const navLinks = document.querySelectorAll(".nav-links"); // get both
const icon = hamburger.querySelector("i");

hamburger.addEventListener("click", () => {
  navLinks.forEach(nav => {
    nav.classList.toggle("show"); // toggle both menus
  });

  // toggle between bars and x
  if (icon.classList.contains("fa-bars")) {
    icon.classList.remove("fa-bars");
    icon.classList.add("fa-xmark");
  } else {
    icon.classList.remove("fa-xmark");
    icon.classList.add("fa-bars");
  }
});
