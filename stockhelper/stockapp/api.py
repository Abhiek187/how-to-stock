import requests
from time import sleep

# Data provided by Financial Modeling Prep: https://financialmodelingprep.com/developer/docs/
API_KEY = "174c8948d0e48bad0418e1fe49d72e15"
FMP = "https://financialmodelingprep.com"
RETRY_LIMIT = 3


def get_request(req_str, retry=0):
    req = requests.get(req_str)
    json = req.json()

    # FMP imposes a rate limit, so check to see if an error occurred
    # Give up after RETRY_LIMIT attempts
    if retry < RETRY_LIMIT and isinstance(json, dict) and "X-Rate-Limit-Retry-After-Milliseconds" in json:
        # Use X-Rate-Limit-Retry-After-Seconds and X-Rate-Limit-Retry-After-Milliseconds to
        # determine how long to sleep for before retrying
        secs = json.get("X-Rate-Limit-Retry-After-Seconds", 0)
        msecs = json["X-Rate-Limit-Retry-After-Milliseconds"]
        sleep(secs + msecs / 1000)
        return get_request(req_str, retry + 1)

    return json


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
        search_str += f"&isEtf=true"  # works better than exchange=etf
    elif exchange != "Any":
        search_str += f"&exchange={exchange}"

    return get_request(search_str)


def get_company_profile(ticker):
    return get_request(f"{FMP}/api/v3/profile/{ticker}?apikey={API_KEY}")


def get_stock_history(ticker):
    return get_request(f"{FMP}/api/v3/historical-price-full/{ticker}?apikey={API_KEY}&serietype=line")
