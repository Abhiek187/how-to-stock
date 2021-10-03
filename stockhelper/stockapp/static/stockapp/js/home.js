const pageTitle = document.title.split(" | ")[0]; // the part to the left of | How to Stock
const equity = document.querySelector(".equity");

if (document.location.pathname.includes("stockapp")) {
    // Make the clicked link active and remove the active class from the previous link
    if (!pageTitle.includes("Home")) {
        const homeLink = document.querySelector(".link-home");
        homeLink.classList.remove("active");
        homeLink.removeAttribute("aria-current");
        let activeLink;

        // The class name matches the title name, but in lowercase
        if (pageTitle.includes("Details")) {
            activeLink = document.querySelector(".link-screener");
        } else {
            activeLink = document.querySelector(
                `.link-${pageTitle.toLowerCase()}`
            );
        }

        activeLink.classList.add("active");
        // Tell screen readers this is the current page
        activeLink.setAttribute("aria-current", "page");
    } else {
        // Initialize the popovers (only on the home page)
        new bootstrap.Popover(equity);
    }
}
