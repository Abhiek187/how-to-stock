from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views import generic

from . import api
from .forms import ScreenerForm
from .models import Card, Stock
from http import HTTPStatus
import json

def get_index(request):
    # Aggregate all the terms needed for each page
    terms = {
        "equity": Card.objects.get(word="Equity")
    }

    return render(request, "stockapp/index.html", {"terms": terms})

def get_stocks(request):
    if request.method == "POST":
        # Keep the form as is after submitting
        form = ScreenerForm(request.POST)

        if form.is_valid() and form.is_bound:
            # Query the dataset
            stock_data = api.get_stocks(form.cleaned_data)
            request.session["results"] = stock_data
            # Return an HttpResponseRedirect to prevent the data from being posted twice
            return HttpResponseRedirect(reverse("stockapp:screener"))

    # Show an empty form when entering the screener page
    form = ScreenerForm()
    # Display the results after a POST request
    results = request.session.get("results")  # results will be None if there aren't any results
    request.session.pop("results", None)  # don't throw an error if the key isn't present

    terms = {
        "beta": Card.objects.get(word="Beta"),
        "dividendYield": Card.objects.get(word="Dividend Yield"),
        "etf": Card.objects.get(word="ETF"),
        "index": Card.objects.get(word="Index"),
        "indexFund": Card.objects.get(word="Index Fund"),
        "marketCap": Card.objects.get(word="Market Cap"),
        "marketExchange": Card.objects.get(word="Market Exchange"),
        "mutualFund": Card.objects.get(word="Mutual Fund"),
        "sharePrice": Card.objects.get(word="Share Price"),
        "volume": Card.objects.get(word="Volume")
    }

    return render(request, "stockapp/screener.html", {
        "form": form,
        "results": results,
        "terms": terms
    })

def get_stock_details(request, ticker):
    if request.method == "POST":
        # Add the stock to the Stocks object
        # Since this isn't form data, the request body needs to be decoded
        stock_info = json.loads(request.body)
        symbol = stock_info.get("ticker")
        name = stock_info.get("name")
        is_buying = stock_info.get("isBuying")
        shares = stock_info.get("shares")
        price = stock_info.get("price")
        change = stock_info.get("change")

        # Read: show all the stocks the user bought (done in the portfolio view)
        try:
            existing_stock = Stock.objects.get(pk=symbol)  # the ticker is the primary key

            # Update: buy or sell an existing stock --> update the number of shares
            if is_buying:
                existing_stock.shares += shares
                existing_stock.save()
            elif shares == existing_stock.shares:
                # Delete: sell all the shares of a stock --> delete it from the portfolio
                existing_stock.delete()
            elif shares > existing_stock.shares:
                # Error: the user sold too many shares
                return JsonResponse(
                    {"status": "failure", "maxShares": existing_stock.shares},
                    status=HTTPStatus.BAD_REQUEST # status code 400 = client-side error
                )
            else:
                existing_stock.shares -= shares
                existing_stock.save()
        except ObjectDoesNotExist:
            # If .get() throws an error
            if is_buying:
                # Create: a new stock is bought --> create the object and add it to the portfolio
                new_stock = Stock(ticker=symbol, name=name, shares=shares, price=price, change=change)
                new_stock.save()
            else:
                # Error: the user can't sell any shares
                return JsonResponse({"status": "failure", "maxShares": 0},
                    status=HTTPStatus.BAD_REQUEST)

        # Update the balance (it should already be defined from the GET request)
        if is_buying:
            request.session["balance"] -= shares * price
        else:
            request.session["balance"] += shares * price

        return JsonResponse({"status": "success"})

    # Fetch details about a company and display it to the user
    profile = api.get_company_profile(ticker) # returns a list of dicts
    history = api.get_stock_history(ticker)  # returns a dict with symbol and historical list

    terms = {
        "beta": Card.objects.get(word="Beta"),
        "broker": Card.objects.get(word="Broker"),
        "dividendYield": Card.objects.get(word="Dividend Yield"),
        "marketCap": Card.objects.get(word="Market Cap"),
        "marketExchange": Card.objects.get(word="Market Exchange"),
        "marketOrder": Card.objects.get(word="Market Order"),
        "risk": Card.objects.get(word="Risk"),
        "trader": Card.objects.get(word="Trader"),
        "volatility": Card.objects.get(word="Volatility"),
        "volume": Card.objects.get(word="Volume")
    }

    if "balance" not in request.session:
        request.session["balance"] = 10000

    return render(request, "stockapp/detail.html", {
        "profile": profile[0],
        "history": history["historical"],
        "balance": request.session["balance"],
        "terms": terms
    })

class FlashCardsView(generic.ListView):
    model = Card
    template_name = "stockapp/flashcards.html"
    context_object_name = "cards"

    def get_queryset(self):
        """
        Sort the cards alphabetically
        """
        return Card.objects.order_by("word")

def get_portfolio(request):
    # The starting balance is $10,000
    if "balance" not in request.session:
        request.session["balance"] = 10000

    terms = {
        "portfolio": Card.objects.get(word="Portfolio"),
        "roi": Card.objects.get(word="ROI"),
        "sharePrice": Card.objects.get(word="Share Price")
    }

    return render(request, "stockapp/portfolio.html", {
        "balance": request.session["balance"],
        "stocks": Stock.objects.all(),
        "terms": terms
    })

# A view only meant to retrieve the balance through a GET request
# https://stackoverflow.com/a/36073883
class SessionBalanceView(generic.base.TemplateView):
    def get(self, request):
        return HttpResponse(request.session.get("balance", 10000))

# Get the price and change of all the stocks in the portfolio
class PricesView(generic.base.TemplateView):
    def get(self, request):
        # Add the current balance with the value of each stock to calculate the user's net worth
        net_worth = request.session.get("balance", 10000)

        # Keep each stock price and change up-to-date
        for stock in Stock.objects.all():
            profile = api.get_company_profile(stock.ticker)[0]
            stock.price = profile["price"]
            stock.change = profile["changes"]
            stock.save()
            net_worth += stock.shares * stock.price

        return JsonResponse({
            "netWorth": net_worth,
            # Only retrieve the price and change column and convert the QuerySet to a list
            "prices": list(Stock.objects.all().values("price", "change"))
        })
