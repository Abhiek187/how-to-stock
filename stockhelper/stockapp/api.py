import dotenv
import os
from pathlib import Path
import requests
from time import sleep

BASE_DIR = Path(__file__).resolve().parent.parent
dotenv_file = os.path.join(BASE_DIR, ".env")
if os.path.isfile(dotenv_file):
    dotenv.load_dotenv(dotenv_file)

# Data provided by Financial Modeling Prep: https://site.financialmodelingprep.com/developer/docs
API_KEY = os.environ["FMP_API_KEY"]
FMP = "https://financialmodelingprep.com/stable"
RETRY_LIMIT = 100

# Source: https://site.financialmodelingprep.com/developer/docs#historical-price-eod-full
# Excluded delisted symbols: VIAC (Viacom), TWTR (Twitter)
FREE_TIER_SYMBOLS = {
    "AAPL": "Apple Inc.",
    "TSLA": "Tesla, Inc.",
    "AMZN": "Amazon.com, Inc.",
    "MSFT": "Microsoft Corporation",
    "NVDA": "NVIDIA Corporation",
    "GOOGL": "Alphabet Inc.",
    "META": "Meta Platforms, Inc.",
    "NFLX": "Netflix, Inc.",
    "JPM": "JPMorgan Chase & Co.",
    "V": "Visa Inc.",
    "BAC": "Bank of America Corporation",
    "AMD": "Advanced Micro Devices, Inc.",
    "PYPL": "PayPal Holdings, Inc.",
    "DIS": "The Walt Disney Company",
    "T": "AT&T Inc.",
    "PFE": "Pfizer, Inc.",
    "COST": "Costco Wholesale Corporation",
    "INTC": "Intel Corporation",
    "KO": "The Coca-Cola Company",
    "TGT": "Target Corporation",
    "NKE": "Nike, Inc.",
    "SPY": "SPDR S&P 500 ETF Trust",
    "BA": "The Boeing Company",
    "BABA": "Alibaba Group Holding Limited",
    "XOM": "Exxon Mobil Corporation",
    "WMT": "Walmart Inc.",
    "GE": "General Electric Company",
    "CSCO": "Cisco Systems, Inc.",
    "VZ": "Verizon Communications Inc.",
    "JNJ": "Johnson & Johnson",
    "CVX": "Chevron Corporation",
    "PLTR": "Palantir Technologies Inc.",
    "SQ": "Block, Inc.",
    "SHOP": "Shopify Inc.",
    "SBUX": "Starbucks Corporation",
    "SOFI": "SoFi Technologies, Inc.",
    "HOOD": "Robinhood Markets, Inc.",
    "RBLX": "Roblox Corporation",
    "SNAP": "Snap Inc.",
    "UBER": "Uber Technologies, Inc.",
    "FDX": "FedEx Corporation",
    "ABBV": "AbbVie Inc.",
    "ETSY": "Etsy, Inc.",
    "MRNA": "Moderna, Inc.",
    "LMT": "Lockheed Martin Corporation",
    "GM": "General Motors Company",
    "F": "Ford Motor Company",
    "RIVN": "Rivian Automotive, Inc.",
    "LCID": "Lucid Group, Inc.",
    "CCL": "Carnival Corporation & plc",
    "DAL": "Delta Air Lines, Inc.",
    "UAL": "United Airlines Holdings, Inc.",
    "AAL": "American Airlines Group Inc.",
    "TSM": "Taiwan Semiconductor Manufacturing Company Limited",
    "SONY": "Sony Group Corporation",
    "ET": "Energy Transfer LP",
    "NOK": "Nokia Corporation",
    "MRO": "Marathon Oil Corporation",
    "COIN": "Coinbase Global, Inc.",
    "SIRI": "Sirius XM Holdings Inc.",
    "RIOT": "Riot Platforms, Inc.",
    "CPRX": "Catalyst Pharmaceuticals, Inc.",
    "VWO": "Vanguard FTSE Emerging Markets ETF",
    "SPYG": "SPDR Portfolio S&P 500 Growth ETF",
    "ROKU": "Roku, Inc.",
    "ATVI": "Activision Blizzard, Inc.",
    "BIDU": "Baidu, Inc.",
    "DOCU": "DocuSign, Inc.",
    "ZM": "Zoom Video Communications, Inc.",
    "PINS": "Pinterest, Inc.",
    "TLRY": "Tilray Brands, Inc.",
    "WBA": "Walgreens Boots Alliance, Inc.",
    "MGM": "MGM Resorts International",
    "NIO": "NIO Inc.",
    "C": "Citigroup Inc.",
    "GS": "The Goldman Sachs Group, Inc.",
    "WFC": "Wells Fargo & Company",
    "ADBE": "Adobe Inc.",
    "PEP": "PepsiCo, Inc.",
    "UNH": "UnitedHealth Group Incorporated",
    "CARR": "Carrier Global Corporation",
    "FUBO": "fuboTV Inc.",
    "HCA": "HCA Healthcare, Inc.",
    "BILI": "Bilibili Inc.",
    "RKT": "Rocket Companies, Inc."
}


def get_request(req_str, retry=0):
    req = requests.get(req_str)

    try:
        json = req.json()
    except requests.exceptions.JSONDecodeError:
        return req.text

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
    search_str = (f"{FMP}/company-screener?apikey={API_KEY}&{price_relation}={price_value}"
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
    return get_request(f"{FMP}/profile?apikey={API_KEY}&symbol={ticker}")


def get_stock_history(ticker):
    return get_request(f"{FMP}/historical-price-eod/full?apikey={API_KEY}&symbol={ticker}")
