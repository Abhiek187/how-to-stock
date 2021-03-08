const flashcards = document.querySelectorAll(".flashcard");

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
