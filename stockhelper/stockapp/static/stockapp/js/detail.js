const ticker = document.querySelector(".symbol").textContent;
const name = document.querySelector(".company-name").textContent;
const priceDom = document.querySelector(".current-price");
const sharePrice = parseFloat(priceDom.textContent.split("$")[1]);
const changeDom = document.querySelector(".change");
const change = parseFloat(changeDom.textContent);

const shortCtx = document.getElementById("short-chart").getContext("2d");
const shortStatsDom = document.querySelector(".short-stats-container");
const shortPredictDom = document.querySelector(".short-predict");
const longCtx = document.getElementById("long-chart").getContext("2d");
const longStatsDom = document.querySelector(".long-stats-container");
const longPredictDom = document.querySelector(".long-predict");

const stockForm = document.querySelector(".stock-form");
const transaction = document.querySelector("#select-transaction");
const shares = document.querySelector("#input-shares");
const balanceResult = document.querySelector(".balance-result");
const balanceDiff = document.querySelector(".balance-diff");

const historyData = JSON.parse(document.getElementById("history-data").textContent);

const shortTermLength = (52 / 12 * 5) >> 0; // average # of weekdays per month
const shortTermData = historyData.slice(0, shortTermLength).reverse();
const shortTermDates = shortTermData.map(data => data.date);
const shortTermPrices = shortTermData.map(data => data.close);

const longTermLength = 52 * 5; // average # of weekdays per year
const longTermData = historyData.slice(0, longTermLength).reverse();
const longTermDates = longTermData.map(data => data.date);
const longTermPrices = longTermData.map(data => data.close);

// https://stackoverflow.com/a/11832950 & https://stackoverflow.com/a/6134070
const round = (number, places) =>
    (Math.round((number + Number.EPSILON) * (10 ** places)) / (10 ** places)).toFixed(places);

// Make the change text green or red depending on its sign
if (parseFloat(changeDom.textContent) < 0) {
    changeDom.innerHTML = `&#x25bc; ${changeDom.textContent}`;
    changeDom.classList.add("text-danger");
} else {
    changeDom.innerHTML = `&#x25b2; ${changeDom.textContent}`;
    changeDom.classList.add("text-success");
}

const checkShares = () => {
    // Show the user's new balance and how much they would be earning or losing
    const isBuying = transaction.value === "buy";
    const numShares = parseInt(shares.value);
    const diff = sharePrice * numShares;
    let newBalance;

    if (isBuying) {
        balanceDiff.textContent = `-$${round(diff, 2)}`;
        balanceDiff.classList.remove("text-success");
        balanceDiff.classList.add("text-danger");
        newBalance = 10000 - diff;
    } else {
        balanceDiff.textContent = `+$${round(diff, 2)}`;
        balanceDiff.classList.remove("text-danger");
        balanceDiff.classList.add("text-success");
        newBalance = 10000 + diff;
    }

    balanceResult.textContent = `New Balance: $${round(newBalance, 2)}`;

    if (newBalance < 0) {
        shares.setCustomValidity("You don't have enough money to buy that many shares.");
    } else if (!isBuying && numShares > 100) {
        shares.setCustomValidity("You can only sell up to 100 shares");
    } else {
        shares.setCustomValidity("");
    }

    return [isBuying, numShares];
};

const showToastMessage = (isError, isBuying, numShares, symbol) => {
    const toast = document.querySelector(".toast");
    toast.classList.add("show");
    const toastBody = toast.querySelector(".toast-body");

    if (isError) {
        toast.classList.remove("bg-success", "text-light");
        toast.classList.add("bg-danger", "text-dark");
        toastBody.textContent = `Server Error: Couldn't ${isBuying ? "buy" : "sell"} shares`;
    } else {
        toast.classList.remove("bg-danger", "text-dark");
        toast.classList.add("bg-success", "text-light");
        toastBody.textContent =
            `Successfully ${isBuying ? "bought" : "sold"} ${numShares} shares from ${symbol}!`;
    }

    // Activate the event listener for closing the toast
    const toastClose = toast.querySelector(".toast-close");
    toastClose.addEventListener("click", () => {
        toast.classList.remove("show");
    });
};

// Show the validation messages as soon as the fields are edited
shares.oninput = checkShares;

stockForm.addEventListener("submit", async event => {
    event.preventDefault(); // don't reload the page
    const token = document.querySelector("input[name='csrfmiddlewaretoken']").value;
    // Make sure the form input is valid
    const [isBuying, numShares] = checkShares();

    // The input is valid, so collect all the data to send to Django
    const stockData = {
        ticker,
        name,
        isBuying,
        shares: numShares,
        price: sharePrice,
        change,
        csrfmiddlewaretoken: token
    };

    try {
        // Make a POST request to add the stock to the Stocks object
        const req = await fetch(window.location.pathname, {
            method: "POST",
            credentials: "same-origin",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": token
            },
            body: JSON.stringify(stockData)
        });

        // Wait for a response, then show a toast that confirms if the stock was added
        const resp = await req.json();

        if (resp.message === "success") {
            showToastMessage(false, isBuying, numShares, ticker);
        } else {
            showToastMessage(true, isBuying, numShares, ticker);
        }
    } catch (error) {
        console.error(`Error: ${error}`);
        showToastMessage(true, isBuying, numShares, ticker);
    }
});

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
    // dom[0] is for predictions
    const [_, mean, variance, std, err, min, max, iqr] = dom.children;
    mean.innerHTML = `<strong>Mean:</strong> ${stats.mean}`;
    variance.innerHTML = `<strong>Variance:</strong> ${stats.variance}`;
    std.innerHTML = `<strong>Standard Deviation:</strong> ${stats.standardDeviation}`;
    err.innerHTML = `<strong>Standard Error:</strong> ${stats.standardError}`;
    min.innerHTML = `<strong>Min:</strong> ${stats.min}`;
    max.innerHTML = `<strong>Max:</strong> ${stats.max}`;
    iqr.innerHTML = `<strong>IQR:</strong> ${stats.iqr}`;
};

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
    dom.innerHTML = `<strong>Predicted Price:</strong> $${round(stats.mean, 2)} (Probability: ${prob})`;
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
