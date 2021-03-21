const netWorthDom = document.querySelector(".net-worth");
const tableRows = document.querySelectorAll(".table-row");
const stockChanges = document.querySelectorAll(".stock-change");

const startingBalance = 10000;
// Remove the $ and commas before parsing the net worth
const netWorth = parseFloat(netWorthDom.textContent.replace(/[,\$]/g, ""));
const netWorthChange = netWorth - startingBalance;

// Show 25b2 for up arrow and 25bc for down arrow
if (netWorthDom < startingBalance) {
    netWorthDom.classList.add("text-danger");
    netWorthDom.innerHTML += ` &#x25bc; $${-netWorthChange}`;
} else {
    netWorthDom.classList.add("text-success");
    netWorthDom.innerHTML += ` &#x25b2; $${netWorthChange}`;
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
