const roiAlert = document.querySelector(".roi-alert");
const portfolio = document.querySelector(".portfolio");
const roi = document.querySelector(".roi");
const portfolioStatus = document.querySelector(".portfolio-status");
const netWorthDom = document.querySelector(".net-worth");
const sharePrice = document.querySelector(".share-price");
const tableRows = document.querySelectorAll(".table-row");
const stockChanges = document.querySelectorAll(".stock-change");

// https://stackoverflow.com/a/11832950 & https://stackoverflow.com/a/6134070
const round = (number, places) =>
    (Math.round((number + Number.EPSILON) * (10 ** places)) / (10 ** places)).toFixed(places);

const startingBalance = 10000;
// Remove the $ and commas before parsing the net worth
const netWorth = parseFloat(netWorthDom.textContent.replace(/[,\$]/g, ""));
const netWorthChange = netWorth - startingBalance;

new bootstrap.Popover(portfolio);
new bootstrap.Popover(roi);

// Give the user feedback on how well their investment is going
if (netWorthChange > 0) {
    portfolioStatus.textContent = "Right now, you're making a profit. Keep up the good work!";
    roiAlert.classList.remove("alert-info");
    roiAlert.classList.add("alert-success");
} else if (netWorthChange < 0) {
    portfolioStatus.textContent = "Right now, you have a net loss. Consider selling stocks that are" +
        " falling or buying stocks that are on the rise.";
    roiAlert.classList.remove("alert-info");
    roiAlert.classList.add("alert-danger");
}

// Show 25b2 for an up arrow and 25bc for a down arrow
if (netWorthChange < 0) {
    netWorthDom.classList.add("text-danger");
    netWorthDom.innerHTML += ` &#x25bc; $${-round(netWorthChange, 2)}`;
} else {
    netWorthDom.classList.add("text-success");
    netWorthDom.innerHTML += ` &#x25b2; $${round(netWorthChange, 2)}`;
}

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
