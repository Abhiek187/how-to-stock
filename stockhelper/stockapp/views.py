from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views import generic

from . import api
from .forms import ScreenerForm
from .models import Card, Portfolio, Stock
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

        # Check if the form is bound to data and doesn't have any errors
        if form.is_valid():
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
        # Make changes to the user's shares
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
            existing_stock = Stock.objects.get(ticker=symbol)
            existing_portfolio = Portfolio.objects.get(
                user=request.user, stock=existing_stock)

            # Update: buy or sell an existing stock --> update the number of shares
            if is_buying:
                existing_portfolio.shares += shares
                existing_portfolio.save()
            elif shares == existing_portfolio.shares:
                # Delete: sell all the shares of a stock --> delete it from the portfolio
                existing_portfolio.delete()
            elif shares > existing_portfolio.shares:
                # Error: the user sold too many shares
                return JsonResponse(
                    {"status": "failure", "maxShares": existing_portfolio.shares},
                    status=HTTPStatus.BAD_REQUEST  # status code 400 = client-side error
                )
            else:
                existing_portfolio.shares -= shares
                existing_portfolio.save()
        except Stock.DoesNotExist:
            # If Stock.get() throws an error
            if is_buying:
                # Create: a new stock is bought --> create the Stock and Portfolio objects
                new_stock = Stock.objects.create(
                    ticker=symbol, name=name, price=price, change=change)
                Portfolio.objects.create(
                    user=request.user, stock=new_stock, shares=shares)
            else:
                # Error: the user can't sell any shares
                return JsonResponse({"status": "failure", "maxShares": 0},
                                    status=HTTPStatus.BAD_REQUEST)
        except Portfolio.DoesNotExist:
            # If Portfolio.get() throws an error
            if is_buying:
                # Create: a new stock is bought --> create the portfolio and add the existing stock
                Portfolio.objects.create(
                    user=request.user, stock=existing_stock, shares=shares)
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
        # Show an error if the ticker is invalid
        "profile": None if not profile else profile[0],
        "history": ticker if not history else history["historical"],
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

    # Join the ticker, name, and shares into one QuerySet
    # stock__ticker = stock.ticker
    portfolios = Portfolio.objects.filter(user=request.user).values(
        "stock__ticker", "stock__name", "shares")

    return render(request, "stockapp/portfolio.html", {
        "balance": request.user.balance,
        "portfolios": portfolios,
        "terms": terms
    })


# A view only meant to retrieve the balance through a GET request
# https://stackoverflow.com/a/36073883
class SessionBalanceView(LoginRequiredMixin, generic.base.TemplateView):
    def get(self, request):
        return HttpResponse(request.user.balance)


# Get the price and change of all the stocks in the portfolio
class PricesView(LoginRequiredMixin, generic.base.TemplateView):
    def get(self, request):
        # Add the current balance with the value of each stock to calculate the user's net worth
        net_worth = request.user.balance
        # Keep track of the price and change of each stock the user owns
        prices = []

        # Keep each stock price and change up-to-date
        # Use select_related to cache the stock foreign key to avoid hitting the database twice
        for portfolio in Portfolio.objects.filter(user=request.user).select_related("stock"):
            stock = portfolio.stock
            profile = api.get_company_profile(stock.ticker)[0]
            stock.price = profile["price"]
            stock.change = profile["changes"]
            stock.save()
            net_worth += Decimal(portfolio.shares * stock.price)
            prices.append({"price": stock.price, "change": stock.change})

        return JsonResponse({
            "netWorth": net_worth,
            "prices": prices
        })
