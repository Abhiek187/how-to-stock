const title = document.title;
const equity = document.querySelector(".equity");

// Make the clicked link active and remove the active class from the previous link
if (title !== "How to Stock") {
    const homeLink = document.querySelector(".link-home");
    homeLink.classList.remove("active");
    homeLink.removeAttribute("aria-current");
    let activeLink;

    // The class name matches the title name, but in lowercase
    if (title.includes("Details")) {
        activeLink = document.querySelector(".link-screener");
    } else {
        activeLink = document.querySelector(`.link-${title.toLowerCase()}`);
    }

    activeLink.classList.add("active");
    // Tell screen readers this is the current page
    activeLink.setAttribute("aria-current", "page");
} else {
    // Initialize the popovers (only on the home page)
    new bootstrap.Popover(equity);
}
