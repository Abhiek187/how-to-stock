const tableRows = document.querySelectorAll(".table-row");

for (const row of tableRows) {
    // Allow each row to be clickable
    const symbol = row.firstElementChild.textContent;
    row.onclick = () =>
        window.open(`${window.location.origin}/stockapp/details/${symbol}`, "_blank",
            rel="noopener noreferrer");
}
