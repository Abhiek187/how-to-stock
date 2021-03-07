const title = document.title;
const flashcards = document.querySelectorAll(".flashcard");

// Make the clicked link active and remove the active class from the previous link
if (title !== "How to Stocks") {
    const homeLink = document.querySelector(".link-home");
    homeLink.classList.remove("active");
    homeLink.removeAttribute("aria-current");

    // The class name matches the title name, but in lowercase
    const activeLink = document.querySelector(`.link-${title.toLowerCase()}`);
    activeLink.classList.add("active");
    // Tell screen readers this is the current page
    activeLink.setAttribute("aria-current", "page");
}

for (const card of flashcards) {
    card.addEventListener("click", event => {
        // Toggle between viewing the word and the definition
        const word = card.querySelector(".word");
        const definition = card.querySelector(".definition");

        if (word.classList.contains("hidden")) {
            word.classList.add("fade-in");
            word.classList.remove("fade-out");
            definition.classList.add("fade-out");
            definition.classList.remove("fade-in");
        } else {
            word.classList.add("fade-out");
            word.classList.remove("fade-in");
            definition.classList.add("fade-in");
            definition.classList.remove("fade-out");
        }

        word.classList.toggle("hidden");
        definition.classList.toggle("hidden");
    });
}
