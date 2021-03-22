import requests

# Data provided by Financial Modeling Prep: https://financialmodelingprep.com/developer/docs/
API_KEY = "174c8948d0e48bad0418e1fe49d72e15"
FMP = "https://financialmodelingprep.com"

def get_stocks(form_data):
    # Collect the form data
    country = form_data["country"]
    price_relation = "priceMoreThan" if form_data["price_relation"] == ">" else "priceLowerThan"
    price_value = form_data["price_value"]
    sector = form_data["sector"]
    exchange = form_data["exchange"]

    # Prepare the API call
    search_str = (f"{FMP}/api/v3/stock-screener?apikey={API_KEY}&{price_relation}={price_value}"
                  f"&isActivelyTrading=true&country={country}&limit=10")

    # Add any optional filters
    if sector != "Any":
        search_str += f"&sector={sector}"

    if exchange == "etf":
        search_str += f"&isEtf=true" # works better than exchange=etf
    elif exchange != "Any":
        search_str += f"&exchange={exchange}"

    req = requests.get(search_str)
    return req.json()

def get_company_profile(ticker):
    req = requests.get(f"{FMP}/api/v3/profile/{ticker}?apikey={API_KEY}")
    return req.json()

def get_stock_history(ticker):
    req = requests.get(f"{FMP}/api/v3/historical-price-full/{ticker}?apikey={API_KEY}&serietype=line")
    return req.json()
