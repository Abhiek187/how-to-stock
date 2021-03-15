const stockForm = document.querySelector(".stock-form");
const regionSelect = document.querySelector(".region-select");
const priceRelationSelect = document.querySelector(".price-relation-select");
const priceNumInput = document.querySelector(".price-num-input");
const sectorSelect = document.querySelector(".sector-select");
const results = document.querySelector(".results");

// stockForm.addEventListener("submit", event => {
//     event.preventDefault(); // don't reload the page

//     // Search for stocks based on the given form values
//     const region = regionSelect.value;
//     const priceRelation = priceRelationSelect.value;
//     const priceNum = priceNumInput.value;
//     const sector = sectorSelect.value;
//     results.textContent = `Searching for stocks in the ${region} ${priceRelation} $${priceNum} in the ${sector} sector...`;
// });

const tableRows = document.querySelectorAll(".table-row");

for (const row of tableRows) {
    const symbol = row.firstElementChild.textContent;
    row.onclick = () => window.open(`${window.location.origin}/stockapp/screener/${symbol}`, "_blank", rel="noopener noreferrer");
}
