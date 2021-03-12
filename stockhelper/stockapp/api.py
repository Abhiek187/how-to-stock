import requests

API_KEY = "174c8948d0e48bad0418e1fe49d72e15"
FMP = "https://financialmodelingprep.com"

def get_stock_data(form_data):
    country = form_data["country"]
    price_relation = "priceMoreThan" if form_data["price_relation"] == ">" else "priceLowerThan"
    price_value = form_data["price_value"]
    sector = form_data["sector"]
    industry = form_data["industry"]

    # [Data provided by Financial Modeling Prep](https://financialmodelingprep.com/developer/docs/)
    req = requests.get(f"{FMP}/api/v3/stock-screener?apikey={API_KEY}&{price_relation}={price_value}"
        f"&isActivelyTrading=true&sector={sector}&industry={industry}&country={country}&limit=10")
    return req.json()
