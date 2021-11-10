const exchangeSelect = document.querySelector(".exchange-select");
const indexAlert = document.querySelector(".index-alert");
const mutualAlert = document.querySelector(".mutual-alert");
const etfAlert = document.querySelector(".etf-alert");

const tableRows = document.querySelectorAll(".table-row");
const marketCap = document.querySelector(".market-cap");
const beta = document.querySelector(".beta");
const sharePrice = document.querySelector(".share-price");
const dividendYield = document.querySelector(".dividend-yield");
const volume = document.querySelector(".volume");
const marketExchange = document.querySelector(".market-exchange");

// Show the appropriate alert for certain exchange options
exchangeSelect.addEventListener("change", (event) => {
    switch (event.target.value) {
        case "nasdaq":
            indexAlert.classList.remove("d-none");
            mutualAlert.classList.add("d-none");
            etfAlert.classList.add("d-none");
            break;
        case "mutual_fund":
            indexAlert.classList.add("d-none");
            mutualAlert.classList.remove("d-none");
            etfAlert.classList.add("d-none");
            break;
        case "etf":
            indexAlert.classList.add("d-none");
            mutualAlert.classList.add("d-none");
            etfAlert.classList.remove("d-none");
            break;
        default:
            indexAlert.classList.add("d-none");
            mutualAlert.classList.add("d-none");
            etfAlert.classList.add("d-none");
    }
});

for (const row of tableRows) {
    // Allow each row to be clickable
    const symbol = row.firstElementChild.textContent;
    row.onclick = () =>
        window.open(
            `${window.location.origin}/stockapp/details/${symbol}`,
            "_blank",
            (rel = "noopener noreferrer")
        );
}

// Initialize all the popovers if the table is present
if (tableRows.length > 0) {
    new bootstrap.Popover(marketCap);
    new bootstrap.Popover(beta);
    new bootstrap.Popover(sharePrice);
    new bootstrap.Popover(dividendYield);
    new bootstrap.Popover(volume);
    new bootstrap.Popover(marketExchange);
}
