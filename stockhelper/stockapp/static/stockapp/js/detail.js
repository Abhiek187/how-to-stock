const shortCtx = document.getElementById("short-chart").getContext("2d");
const longCtx = document.getElementById("long-chart").getContext("2d");
const historyData = JSON.parse(document.getElementById("history-data").textContent);

const shortTermLength = (52 / 12 * 5) >> 0; // average # of weekdays per month
const shortTermData = historyData.slice(0, shortTermLength).reverse();
const shortTermDates = shortTermData.map(data => data.date);
const shortTermPrices = shortTermData.map(data => data.close);

const longTermLength = 52 * 5; // average # of weekdays per year
const longTermData = historyData.slice(0, longTermLength).reverse();
const longTermDates = longTermData.map(data => data.date);
const longTermPrices = longTermData.map(data => data.close);

// const chart = new Chart(ctx, {
//     // The type of chart we want to create
//     type: "line",

//     // The data for our dataset
//     data: {
//         labels: ["January", "February", "March", "April", "May", "June", "July"],
//         datasets: [{
//             label: "My First dataset",
//             backgroundColor: "rgb(255, 99, 132)",
//             borderColor: "rgb(255, 99, 132)",
//             data: [0, 10, 5, 2, 20, 30, 45]
//         }]
//     },

//     // Configuration options go here
//     options: {}
// });

const shortChart = new Chart(shortCtx, {
    // The type of chart we want to create
    type: "line",

    // The data for our dataset
    data: {
        labels: shortTermDates,
        datasets: [{
            label: "Short-term Prices",
            borderColor: "#00f",
            data: shortTermPrices
        }]
    },

    // Configuration options go here
    options: {}
});

const longChart = new Chart(longCtx, {
    // The type of chart we want to create
    type: "line",

    // The data for our dataset
    data: {
        labels: longTermDates,
        datasets: [{
            label: "Long-term Prices",
            borderColor: "#00f",
            data: longTermPrices
        }]
    },

    // Configuration options go here
    options: {}
});
