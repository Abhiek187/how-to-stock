from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views import generic

from . import api
from .forms import ScreenerForm
from .models import Card, Stock
from decimal import Decimal
from http import HTTPStatus
import json


# Home view
def get_index(request):
    # Aggregate all the terms needed for each page
    terms = {
        "equity": Card.objects.get(word="Equity")
    }

    return render(request, "stockapp/index.html", {
        "terms": terms,
        "user": request.user
    })


# Screener view
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
    # results will be None if there aren't any results
    results = request.session.get("results")
    # don't throw an error if the key isn't present
    request.session.pop("results", None)

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


# Details view
# Users are required to log in if the view requires access to their balance (cookie lasts 2 weeks)
@login_required
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
            # Check if the user already owns this stock
            existing_stock = Stock.objects.get(
                user=request.user, ticker=symbol)

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
                    status=HTTPStatus.BAD_REQUEST  # status code 400 = client-side error
                )
            else:
                existing_stock.shares -= shares
                existing_stock.save()
        except ObjectDoesNotExist:
            # If .get() throws an error
            if is_buying:
                # Create: a new stock is bought --> create the object and add it to the portfolio
                new_stock = Stock(user=request.user, ticker=symbol, name=name,
                                  shares=shares, price=price, change=change)
                new_stock.save()
            else:
                # Error: the user can't sell any shares
                return JsonResponse({"status": "failure", "maxShares": 0},
                                    status=HTTPStatus.BAD_REQUEST)

        # Update the user's balance
        if is_buying:
            request.user.balance -= Decimal(shares * price)
        else:
            request.user.balance += Decimal(shares * price)

        request.user.save()
        return JsonResponse({"status": "success"})

    # Fetch details about a company and display it to the user
    profile = api.get_company_profile(ticker)  # returns a list of dicts
    # returns a dict with symbol and historical list
    history = api.get_stock_history(ticker)

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

    return render(request, "stockapp/detail.html", {
        "profile": profile[0],
        "history": history["historical"],
        "balance": request.user.balance,
        "terms": terms
    })


# Flashcards view
class FlashCardsView(generic.ListView):
    model = Card
    template_name = "stockapp/flashcards.html"
    context_object_name = "cards"

    def get_queryset(self):
        """
        Sort the cards alphabetically
        """
        return Card.objects.order_by("word")


# Portfolio view
@login_required
def get_portfolio(request):
    terms = {
        "portfolio": Card.objects.get(word="Portfolio"),
        "roi": Card.objects.get(word="ROI"),
        "sharePrice": Card.objects.get(word="Share Price")
    }

    return render(request, "stockapp/portfolio.html", {
        "balance": request.user.balance,
        "stocks": Stock.objects.all(),
        "terms": terms
    })


# A view only meant to retrieve the balance through a GET request
# https://stackoverflow.com/a/36073883
class SessionBalanceView(generic.base.TemplateView):
    def get(self, request):
        return HttpResponse(request.user.balance)


# Get the price and change of all the stocks in the portfolio
class PricesView(LoginRequiredMixin, generic.base.TemplateView):
    def get(self, request):
        # Add the current balance with the value of each stock to calculate the user's net worth
        net_worth = request.user.balance

        # Keep each stock price and change up-to-date
        for stock in Stock.objects.all():
            profile = api.get_company_profile(stock.ticker)[0]
            stock.price = profile["price"]
            stock.change = profile["changes"]
            stock.save()
            net_worth += Decimal(stock.shares * stock.price)

        return JsonResponse({
            "netWorth": net_worth,
            # Only retrieve the price and change column and convert the QuerySet to a list
            "prices": list(Stock.objects.all().values("price", "change"))
        })
