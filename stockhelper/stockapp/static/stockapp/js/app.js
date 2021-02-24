const flashcards = document.querySelectorAll(".flashcard");

for (const card of flashcards) {
    card.addEventListener("click", event => {
        console.log(`You clicked on ${event.target.textContent}`);
    });
}
