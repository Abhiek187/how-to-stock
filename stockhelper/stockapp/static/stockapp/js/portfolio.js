// Alert and Money container elements
const roiAlert = document.querySelector(".roi-alert");
const portfolio = document.querySelector(".portfolio");
const roi = document.querySelector(".roi");
const portfolioStatus = document.querySelector(".portfolio-status");
const netWorthDom = document.querySelector(".net-worth");
const netWorthSpinner = document.querySelector(".net-worth-spinner");

// Table elements
const sharePrice = document.querySelector(".share-price");
const tableRows = document.querySelectorAll(".table-row");

// Display monetary values with a dollar sign, commas, and rounded to 2 decimal places
const toMoney = num => `$${num.toLocaleString(undefined, {maximumFractionDigits: 2})}`;

// Asychronously update the price and change of each stock, then update the net worth
const getPriceAndChange = async () => {
    try {
        const req = await fetch(`${window.location.origin}/stockapp/api/prices`);
        const resp = await req.json();
        const {netWorth, prices} = resp;

        // Replace the spinner with the actual value
        netWorthSpinner.remove();
        netWorthDom.textContent = toMoney(netWorth);

        const startingBalance = 10000;
        const netWorthChange = netWorth - startingBalance;

        if (netWorthChange > 0) {
            // Give the user feedback on how well their investment is going
            portfolioStatus.textContent = "Right now, you're making a profit. Keep up the good work!";
            roiAlert.classList.remove("alert-info");
            roiAlert.classList.add("alert-success");

            // Show how much the net worth has changed (25b2 for up arrow and 25bc for down arrow)
            netWorthDom.classList.add("text-success");
            netWorthDom.innerHTML += ` &#x25b2; ${toMoney(netWorthChange)}`;
        } else if (netWorthChange < 0) {
            portfolioStatus.textContent = "Right now, you have a net loss. Consider selling stocks " +
                "that are falling or buying stocks that are on the rise.";
            roiAlert.classList.remove("alert-info");
            roiAlert.classList.add("alert-danger");

            netWorthDom.classList.add("text-danger");
            netWorthDom.innerHTML += ` &#x25bc; ${toMoney(-netWorthChange)}`;
        }

        tableRows.forEach((row, r) => {
            // Remove the spinners and display the price and change for each row
            const stockPrice = row.querySelector(".stock-price");
            const priceSpinner = row.querySelector(".price-spinner");
            priceSpinner.remove();
            stockPrice.textContent = `$${prices[r].price}`;

            const stockChange = row.querySelector(".stock-change");
            const changeSpinner = row.querySelector(".change-spinner");
            changeSpinner.remove();
            const change = prices[r].change;

            // Make the change text green or red depending on its sign
            if (change < 0) {
                stockChange.innerHTML = `&#x25bc; ${-change}`;
                stockChange.classList.add("text-danger");
            } else {
                stockChange.innerHTML = `&#x25b2; ${change}`;
                stockChange.classList.add("text-success");
            }
        });
    } catch (error) {
        console.error(`Error: ${error}`);
    }
};

getPriceAndChange();

new bootstrap.Popover(portfolio);
new bootstrap.Popover(roi);

// Initialize the popovers if the table is present
if (tableRows.length > 0) {
    new bootstrap.Popover(sharePrice);
}

for (const row of tableRows) {
    // Allow each row to be clickable
    const symbol = row.firstElementChild.textContent;
    row.onclick = () =>
        window.open(`${window.location.origin}/stockapp/details/${symbol}`, "_blank",
            rel="noopener noreferrer");
}
