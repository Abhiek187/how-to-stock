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
            print(f"{stock_data=}")

            # If stock_data isn't a list (due to an API error), treat it like there are no results
            if isinstance(stock_data, list):
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
    raw_profile = api.get_company_profile(ticker)  # returns a list of dicts
    # returns a dict with symbol and historical list
    raw_history = api.get_stock_history(ticker)
    print(f"{raw_profile=}")
    print(f"{raw_history=}")

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
    status = 200

    # profile should be an array with one element, display an error if that's not the case
    if not raw_profile:
        profile = None
        status = 400
    elif isinstance(raw_profile, list) and len(raw_profile) >= 1:
        profile = raw_profile[0]
    else:
        profile = raw_profile
        status = 400

    # history should be an array of dicts, display an error if that's not the case
    if isinstance(raw_history, list):
        history = raw_history
    elif isinstance(raw_history, dict) and "Error Message" in raw_history:
        history = raw_history
        status = 400
    else:
        history = ticker
        status = 400

    return render(request, "stockapp/detail.html", {
        "profile": profile,
        "history": history,
        "balance": request.user.balance,
        "terms": terms
    }, status=status)


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


class PriceView(LoginRequiredMixin, generic.base.TemplateView):
    def get(self, request, ticker):
        # Get the price, change, and shares of the given ticker
        # Tickers are stored in all caps, but the request should be case insensitive
        upper_ticker = ticker.upper()

        try:
            # SELECT Stock.price, Stock.change, Porfolio.shares
            # FROM Stock JOIN Portfolio ON Stock.ticker = Porfolio.stock
            # WHERE Stock.ticker = <ticker> AND Porfolio.user =
            # (SELECT username FROM User WHERE username = <request.user>)
            portfolio = Portfolio.objects.get(
                user=request.user, stock=upper_ticker)
            stock = portfolio.stock
            raw_profile = api.get_company_profile(upper_ticker)
            print(f"{raw_profile=}")

            # profile should be an array with one element, display an error if that's not the case
            if not raw_profile:
                return JsonResponse({
                    "error": f"No stock {upper_ticker} found"
                }, status=HTTPStatus.BAD_REQUEST)
            elif isinstance(raw_profile, list) and len(raw_profile) >= 1:
                profile = raw_profile[0]
            else:
                error = raw_profile.get("Error Message", raw_profile) if hasattr(
                    raw_profile, "get") else raw_profile
                return JsonResponse({
                    "error": error
                }, status=HTTPStatus.INTERNAL_SERVER_ERROR)

            # A company could change its name while owning their stock, such as Meta
            stock.name = profile["companyName"]
            stock.price = profile["price"]
            stock.change = profile["change"]
            stock.save()

            return JsonResponse({
                "price": stock.price,
                "change": stock.change,
                "shares": portfolio.shares
            })
        except Portfolio.DoesNotExist:
            return JsonResponse({
                "error": f"{upper_ticker} doesn't exist in the user's porfolio"
            }, status=HTTPStatus.BAD_REQUEST)
