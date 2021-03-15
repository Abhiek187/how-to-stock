const title = document.title;

// Make the clicked link active and remove the active class from the previous link
if (title !== "How to Stocks" && !title.includes("Details")) {
    const homeLink = document.querySelector(".link-home");
    homeLink.classList.remove("active");
    homeLink.removeAttribute("aria-current");

    // The class name matches the title name, but in lowercase
    const activeLink = document.querySelector(`.link-${title.toLowerCase()}`);
    activeLink.classList.add("active");
    // Tell screen readers this is the current page
    activeLink.setAttribute("aria-current", "page");
}
