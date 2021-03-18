const stockChanges = document.querySelectorAll(".stock-change");

for (const change of stockChanges) {
    // Make the change text green or red depending on its sign
    if (parseFloat(change.textContent) < 0) {
        change.innerHTML = `&#x25bc; ${change.textContent}`;
        change.classList.add("text-danger");
    } else {
        change.innerHTML = `&#x25b2; ${change.textContent}`;
        change.classList.add("text-success");
    }
}
