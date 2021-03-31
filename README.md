# How to Stock

<img src="graphs.png" alt="stock graphs" width="1000">

This is a web service that serves as an introduction to the stock market for users new to finance. Users can learn about various financial terms, simulate trading stocks using a virtual balance, and view stock predictions based on probability and statistical data.

## Features

The app is split up into 4 sections:

- **Screener:** This is where users can filter stocks by country, price, sector, and exchange.

- **Flashcards:** Users can view a list of financial terms used throughout the app.

- **Portfolio:** Users can view a list of stocks they've invested in. They start off with $10,000 and can view how their net worth changes each day.

- **Details:** This page shows stock information about a company as well as a detailed analysis of the stock price for short and long-term investments. This is also where users can trade stocks.

## Dependencies

The front-end is created in HTML, CSS, & JS and the back-end is created in [Django](https://docs.djangoproject.com/en/3.1/) and utilizes an SQLite database. [Bootstrap](https://getbootstrap.com/) was used to enhance the site's design and implement UI elements such as alerts and popovers. [Chart.js](https://www.chartjs.org/) was used to visualize the stock trends on the details page. And [Financial Modeling Prep](https://financialmodelingprep.com/developer/docs/) was the API used to implement the screener functionality and obtain detailed profiles and stock history from all the companies. Above everything else, this web app is designed to be responsive, accessible, and thoroughly tested.

## How to Run

After cloning this repo, run the following commands:

1. Create a folder for the virtual environment: `python3 -m venv <folder-name>`
2. Activate the virtual environment: `source <folder-name>/bin/activate`
3. Install all python dependencies: `pip3 install -r requirements.txt`
4. Head into the stockhelper directory: `cd stockhelper`
5. Create the SQLite databases: `python3 manage.py migrate`
6. Load the flashcards data: `python3 manage.py loaddata cards.json`
7. Run the Django server: `python3 manage.py runserver`
8. Open `localhost:8000/stockapp` in your browser.
9. When done, press `CTRL/CMD-C` and deactivate the virtual environment: `deactivate`
