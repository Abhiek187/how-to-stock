const change = document.querySelector(".change");
const shortCtx = document.getElementById("short-chart").getContext("2d");
const shortStatsDom = document.querySelector(".short-stats");
const shortPredictDom = document.querySelector(".short-predict");
const longCtx = document.getElementById("long-chart").getContext("2d");
const longStatsDom = document.querySelector(".long-stats");
const longPredictDom = document.querySelector(".long-predict");
const historyData = JSON.parse(document.getElementById("history-data").textContent);

const shortTermLength = (52 / 12 * 5) >> 0; // average # of weekdays per month
const shortTermData = historyData.slice(0, shortTermLength).reverse();
const shortTermDates = shortTermData.map(data => data.date);
const shortTermPrices = shortTermData.map(data => data.close);

const longTermLength = 52 * 5; // average # of weekdays per year
const longTermData = historyData.slice(0, longTermLength).reverse();
const longTermDates = longTermData.map(data => data.date);
const longTermPrices = longTermData.map(data => data.close);

// Make the change text green or red depending on its sign
if (parseFloat(change.textContent) > 0) {
    change.innerHTML = `&#x25b2; ${change.textContent}`;
    change.classList.add("text-success");
} else {
    change.innerHTML = `&#x25bc; ${change.textContent}`;
    change.classList.add("text-danger");
}

const getStats = prices => {
    // Get the statistical properties of the price array
    const sum = arr => arr.reduce((e1, e2) => e1 + e2, 0);
    const mean = sum(prices) / prices.length;
    const variance = sum(prices.map(price => (price - mean) ** 2)) / (prices.length - 1);
    const standardDeviation = Math.sqrt(variance);
    const standardError = standardDeviation / Math.sqrt(prices.length);
    // ...prices creates a copy of the array
    const min = Math.min(...prices);
    const max = Math.max(...prices);
    // Sort the array and find the first and third quartiles
    const sortedArr = [...prices].sort();
    const q1 = sortedArr[Math.floor(sortedArr.length / 4)];
    const q3 = sortedArr[Math.ceil(sortedArr.length * 3 / 4)];
    const iqr = q3 - q1;

    return {
        mean,
        variance,
        standardDeviation,
        standardError,
        min,
        max,
        iqr
    };
};

const displayStats = (stats, dom) => {
    dom.textContent = `Mean: ${stats.mean}, Variance: ${stats.variance},
    Standard Deviation: ${stats.standardDeviation}, Standard Error: ${stats.standardError},
    Min: ${stats.min}, Max: ${stats.max}, IQR: ${stats.iqr}`;
};

// https://stackoverflow.com/a/11832950
const round = (number, places) =>
    Math.round((number + Number.EPSILON) * (10 ** places)) / (10 ** places);

// Calculate the x value of a normal curve given the mean and standard deviation
const normalProb = (x, mu, sigma) =>
    Math.exp(-((x - mu) ** 2) / (2 * sigma ** 2)) / (sigma * Math.sqrt(2 * Math.PI));

/* p(v|m) = prod(p(mi|v) * p(v), for i in m)
 * p(mi|v): mi is x, v is mu, and sigma is sigma
 * p(v): v is x, mu is mu, and sigma is sigma
 */
const bayesProb = (predictedPrice, pastPrices, stats) => {
    let total = 1;

    for (const price of pastPrices) {
        total *= normalProb(price, predictedPrice, stats.standardDeviation)
            * normalProb(predictedPrice, stats.mean, stats.standardError);
    }

    return total;
};

const displayProb = (prob, stats, dom) => {
    dom.textContent = `Predicted Price: $${round(stats.mean, 2)} (Probability: ${prob})`;
};

// Compute and display the stats for the short-term and long-term
const shortTermStats = getStats(shortTermPrices);
displayStats(shortTermStats, shortStatsDom);
const longTermStats = getStats(longTermPrices);
displayStats(longTermStats, longStatsDom);

// Calculate the most likely price the next day
const shortTermProb = bayesProb(shortTermStats.mean, shortTermPrices, shortTermStats);
displayProb(shortTermProb, shortTermStats, shortPredictDom);
const longTermProb = bayesProb(longTermStats.mean, longTermPrices, longTermStats);
displayProb(longTermProb, longTermStats, longPredictDom);

// for (let i = -1; i < 1; i+=0.1) {
//     console.log(`mu + ${i}: ${bayesProb(shortTermStats.mean + i, shortTermPrices, shortTermStats)}`);
//     console.log(`mu + ${i}: ${bayesProb(longTermStats.mean + i, longTermPrices, longTermStats)}`);
// }

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
