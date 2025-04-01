let map;

document.addEventListener("DOMContentLoaded", function () {
  const toggleButtons = document.querySelectorAll("#criteria-toggle button");

  toggleButtons.forEach((button) => {
    button.addEventListener("click", function () {
      toggleButtons.forEach((btn) =>
        btn.classList.remove("active", "btn-primary")
      );
      toggleButtons.forEach((btn) => btn.classList.add("btn-outline-primary"));

      this.classList.add("active", "btn-primary");
      this.classList.remove("btn-outline-primary");
    });
  });
});

document.querySelectorAll(".view-toggle button").forEach((button) => {
  button.addEventListener("click", function () {
    document
      .querySelectorAll(".view-toggle button")
      .forEach((btn) => btn.classList.remove("active"));
    this.classList.add("active");

    const simpleView = document.querySelector(".simple-view");
    const advancedView = document.querySelector(".advanced-view");

    if (this.dataset.view === "simple") {
      simpleView.style.display = "block";
      advancedView.style.display = "none";
    } else {
      simpleView.style.display = "none";
      advancedView.style.display = "block";
    }
  });
});


function checkScroll() {
  const elements = document.querySelectorAll(".animate-on-scroll");
  elements.forEach((el) => {
    const elementTop = el.getBoundingClientRect().top;
    const windowHeight = window.innerHeight;
    if (elementTop < windowHeight * 0.8) {
      el.classList.add("visible");
    }
  });
}
window.addEventListener("scroll", checkScroll);
checkScroll();
