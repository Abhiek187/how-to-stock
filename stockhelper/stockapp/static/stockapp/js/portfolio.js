const tableRows = document.querySelectorAll(".table-row");
const stockChanges = document.querySelectorAll(".stock-change");

for (const row of tableRows) {
    // Allow each row to be clickable
    const symbol = row.firstElementChild.textContent;
    row.onclick = () =>
        window.open(`${window.location.origin}/stockapp/screener/${symbol}`, "_blank",
            rel="noopener noreferrer");
}

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
