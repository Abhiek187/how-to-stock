# How to Stock

<img src="graphs.png" alt="stock graphs" width="1000">

A web app that can teach users how the stock market works, trade virtual stocks, and view predictions of stocks

## How to Run

After cloning this repo and installing [Django](https://docs.djangoproject.com/en/3.1/), run the following commands:

1. Create a folder for the virtual environment: `python3 -m venv <folder-name>`
2. Activate the virtual environment: `source <folder-name>/bin/activate`
3. Install all python dependencies: `pip3 install -r requirements.txt`
4. Head into the stockhelper directory: `cd stockhelper`
5. Create the SQLite databases: `python3 manage.py migrate`
6. Load the flashcards data: `python3 manage.py loaddata cards.json`
7. Run the Django server: `python3 manage.py runserver`
8. Open `localhost:8000/stockapp` in your browser.
9. When done, press `CTRL/CMD-C` and deactivate the virtual environment: `deactivate`
