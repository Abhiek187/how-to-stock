const flashcards = document.querySelectorAll(".flashcard");

const flipCard = (card) => {
    // Toggle between viewing the word and the definition
    const word = card.querySelector(".word");
    const definition = card.querySelector(".definition");

    if (word.classList.contains("hidden")) {
        // Show the word
        word.classList.add("fade-in");
        word.classList.remove("fade-out");
        definition.classList.add("fade-out");
        definition.classList.remove("fade-in");
        card.ariaLabel = word.textContent;
    } else {
        // Show the definition
        word.classList.add("fade-out");
        word.classList.remove("fade-in");
        definition.classList.add("fade-in");
        definition.classList.remove("fade-out");
        card.ariaLabel = definition.textContent;
    }

    word.classList.toggle("hidden");
    definition.classList.toggle("hidden");
};

for (const card of flashcards) {
    // Flip the card by either clicking it or pressing space or enter
    card.addEventListener("click", () => flipCard(card));
    card.addEventListener("keypress", (event) => {
        if (event.key === " " || event.key === "Enter") {
            event.preventDefault(); // prevent the screen from scrolling down on space
            flipCard(card);
        }
    });
}
