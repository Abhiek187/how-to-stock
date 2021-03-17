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

const sum = arr => arr.reduce((e1, e2) => e1 + e2, 0);

const getStats = prices => {
    // Get the statistical properties of the price array
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

// https://stackoverflow.com/a/11832950 & https://stackoverflow.com/a/6134070
const round = (number, places) =>
    (Math.round((number + Number.EPSILON) * (10 ** places)) / (10 ** places)).toFixed(places);

// Calculate the x value of a normal curve given the mean and standard deviation
const normalProb = (x, mu, sigma) =>
    Math.exp(-((x - mu) ** 2) / (2 * sigma ** 2)) / (sigma * Math.sqrt(2 * Math.PI));

/* p(v|m) = prod(p(mi|v) * p(v), for i in m)
 * p(mi|v): mi is x, v is mu, and se is sigma
 * p(v): v is x, mu is mu, and sigma is sigma
 */
const bayesProb = (predictedPrice, pastPrices, stats) => {
    let total = 1;

    for (const price of pastPrices) {
        total *= normalProb(price, predictedPrice, stats.standardError)
            * normalProb(predictedPrice, stats.mean, stats.standardDeviation);
    }

    return total;
};

const displayProb = (prob, stats, dom) => {
    dom.textContent = `Predicted Price: $${round(stats.mean, 2)} (Probability: ${prob})`;
};

const predictPrice = y => {
    // Perform linear regression to find the best line of fit given the data points
    const n = y.length;
    const x = [...Array(n).keys()];
    const xy = x.map((e, i) => e * y[i]);
    const x2 = x.map(e => e ** 2);
    const y2 = y.map(e => e ** 2);
    /* Formulas from: https://www.statisticshowto.com/probability-and-statistics/regression-analysis
     * /find-a-linear-regression-equation/#FindaLinear
     */
    const m = (n * sum(xy) - sum(x) * sum(y)) / (n * sum(x2) - sum(x) ** 2);
    const b = (sum(y) * sum(x2) - sum(x) * sum(xy)) / (n * sum(x2) - sum(x) ** 2);
    const line = x.map(p => m * p + b);
    return [m, b, line];
};

const displayPred = (m, n, b, dom) => {
    const pred = m * n + b;
    dom.textContent = `Predicted Price: $${round(pred, 2)}`;

    // Show more info about how the price will change while hovering over the price
    if (m < 0) {
        dom.title = `On average, the stock price is decreasing by $${round(-m, 2)} each day.`;
        dom.classList.add("text-danger");
    } else {
        dom.title = `On average, the stock price is increasing by $${round(m, 2)} each day.`;
        dom.classList.add("text-success");
    }
}

// Compute and display the stats for the short-term and long-term
const shortTermStats = getStats(shortTermPrices);
displayStats(shortTermStats, shortStatsDom);
const longTermStats = getStats(longTermPrices);
displayStats(longTermStats, longStatsDom);

// Calculate the most likely price the next day
// const shortTermProb = bayesProb(shortTermStats.mean, shortTermPrices, shortTermStats);
// displayProb(shortTermProb, shortTermStats, shortPredictDom);
// const longTermProb = bayesProb(longTermStats.mean, longTermPrices, longTermStats);
// displayProb(longTermProb, longTermStats, longPredictDom);

const [shortM, shortB, shortLine] = predictPrice(shortTermPrices);
displayPred(shortM, shortTermLength, shortB, shortPredictDom);
const [longM, longB, longLine] = predictPrice(longTermPrices);
displayPred(longM, longTermLength, longB, longPredictDom);

// for (let i = -1; i < 1; i+=0.1) {
//     console.log(`mu + ${i}: ${bayesProb(shortTermStats.mean + i, shortTermPrices, shortTermStats)}`);
//     console.log(`mu + ${i}: ${bayesProb(longTermStats.mean + i, longTermPrices, longTermStats)}`);
// }

// Chart for the short-term data
const shortChart = new Chart(shortCtx, {
    type: "line",

    data: {
        labels: shortTermDates,
        datasets: [
            {
                // Draw the trend line on top of the price graph
                label: "Trend Line",
                backgroundColor: "#000", // black
                borderColor: "#333",
                fill: false, // just show a line
                data: shortLine
            },
            {
                label: "Stock Price",
                backgroundColor: "#00bfff", // deepskyblue
                borderColor: "#00f",
                data: shortTermPrices
            }
        ]

    },

    options: {
        aspectRatio: window.innerWidth < 1200 ? 1.25 : 1.5, // width / height
        scales: {
            xAxes: [{
                scaleLabel: {
                    display: true,
                    labelString: "Date"
                }
            }],
            yAxes: [{
                scaleLabel: {
                    display: true,
                    labelString: "Price ($)"
                }
            }]
        },
        title: {
            display: true,
            fontSize: 18,
            text: "Short-Term Historical Data"
        }
    }
});

// Chart for the long-term data
const longChart = new Chart(longCtx, {
    type: "line",

    data: {
        labels: longTermDates, // x-axis labels
        datasets: [
            {
                // Draw the trend line on top of the price graph
                label: "Trend Line",
                backgroundColor: "#000", // black
                borderColor: "#333",
                fill: false, // just show a line
                data: longLine
            },
            {
                label: "Stock Price",
                backgroundColor: "#00bfff", // deepskyblue
                borderColor: "#00f",
                data: longTermPrices
            }
        ]
    },

    options: {
        aspectRatio: window.innerWidth < 1200 ? 1.25 : 1.5, // width / height
        scales: {
            xAxes: [{
                scaleLabel: {
                    display: true,
                    labelString: "Date"
                },
                ticks: {
                    autoSkipPadding: 5
                }
            }],
            yAxes: [{
                scaleLabel: {
                    display: true,
                    labelString: "Price ($)"
                }
            }]
        },
        title: {
            display: true,
            fontSize: 18,
            text: "Long-Term Historical Data"
        }
    }
});
