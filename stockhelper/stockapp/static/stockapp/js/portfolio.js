// Alert and Money container elements
const roiAlert = document.querySelector(".roi-alert");
const portfolio = document.querySelector(".portfolio");
const roi = document.querySelector(".roi");
const portfolioStatus = document.querySelector(".portfolio-status");
const balance = document.querySelector(".balance");
const netWorthDom = document.querySelector(".net-worth");
const netWorthSpinner = document.querySelector(".net-worth-spinner");

// Table elements
const sharePrice = document.querySelector(".share-price");
const tableRows = document.querySelectorAll(".table-row");

// Display monetary values with a dollar sign, commas, and rounded to 2 decimal places
const toMoney = (num) =>
    `$${parseFloat(num).toLocaleString(undefined, {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
    })}`;

// Parse a money string into a float
const toNum = (str) => parseFloat(str.replace(/[$,]/g, ""));

// Asychronously update the price and change of each stock, then update the net worth
const getPriceAndChange = async () => {
    // Add the current balance with the value of each stock to calculate the user's net worth
    let netWorth = toNum(balance.textContent);

    for (const row of tableRows) {
        const stockTicker = row.querySelector(".stock-ticker");

        try {
            const req = await fetch(
                `${window.location.origin}/stockapp/api/price/${stockTicker.textContent}`
            );
            const resp = await req.json();

            // Remove the spinners
            const stockPrice = row.querySelector(".stock-price");
            const priceSpinner = row.querySelector(".price-spinner");
            const stockChange = row.querySelector(".stock-change");
            const changeSpinner = row.querySelector(".change-spinner");
            priceSpinner.remove();
            changeSpinner.remove();

            // Show an error if the request failed
            if (resp.error !== undefined) {
                stockPrice.textContent = "Error";
                stockPrice.classList.add("text-danger");
                stockChange.textContent = resp.error;
                stockChange.classList.add("text-danger");
            } else {
                const { price, change, shares } = resp;
                netWorth += shares * price;

                // Display the price and change for each row
                stockPrice.textContent = `$${price}`;

                // Make the change text green or red depending on its sign
                if (change < 0) {
                    stockChange.innerHTML = `&#x25bc; ${-change}`;
                    stockChange.classList.add("text-danger");
                } else {
                    stockChange.innerHTML = `&#x25b2; ${change}`;
                    stockChange.classList.add("text-success");
                }
            }
        } catch (error) {
            console.error(`Error: ${error}`);
        }
    }

    // Replace the spinner with the actual value
    netWorthSpinner.remove();
    netWorthDom.textContent = toMoney(netWorth);

    const startingBalance = 10000;
    const netWorthChange = netWorth - startingBalance;

    if (netWorthChange > 0) {
        // Give the user feedback on how well their investment is going
        portfolioStatus.textContent =
            "Right now, you're making a profit. Keep up the good work!";
        roiAlert.classList.remove("alert-info");
        roiAlert.classList.add("alert-success");

        // Show how much the net worth has changed (25b2 for up arrow and 25bc for down arrow)
        netWorthDom.classList.add("text-success");
        netWorthDom.innerHTML += ` &#x25b2; ${toMoney(netWorthChange)}`;
    } else if (netWorthChange < 0) {
        portfolioStatus.textContent =
            "Right now, you have a net loss. Consider selling stocks " +
            "that are falling or buying stocks that are on the rise.";
        roiAlert.classList.remove("alert-info");
        roiAlert.classList.add("alert-danger");

        netWorthDom.classList.add("text-danger");
        netWorthDom.innerHTML += ` &#x25bc; ${toMoney(-netWorthChange)}`;
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
        window.open(
            `${window.location.origin}/stockapp/details/${symbol}`,
            "_blank",
            (rel = "noopener noreferrer")
        );
}
