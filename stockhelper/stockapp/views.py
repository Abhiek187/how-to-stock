from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import generic

from . import api
from .forms import ScreenerForm
from .models import Card, Dummy, Stock
import json

class IndexView(generic.ListView):
    model = Dummy
    template_name = "stockapp/index.html"

def get_stocks(request):
    if request.method == "POST":
        # Keep the form as is after submitting
        form = ScreenerForm(request.POST)

        if form.is_valid() and form.is_bound:
            # Query the dataset
            stock_data = api.get_stock_data(form.cleaned_data)
            request.session["results"] = stock_data
            # Return an HttpResponseRedirect to prevent the data from being posted twice
            return HttpResponseRedirect(reverse("stockapp:screener"))

    # Show an empty form when entering the screener page
    form = ScreenerForm()
    # Display the results after a POST request
    results = request.session.get("results")  # results will be None if there aren't any results
    request.session.pop("results", None)  # don't throw an error if the key isn't present
    return render(request, "stockapp/screener.html", {"form": form, "results": results})

def get_stock_details(request, ticker):
    if request.method == "POST":
        # Add the stock to the Stocks object
        # Since this isn't form data, the request body needs to be decoded
        stock_info = json.loads(request.body)
        symbol = stock_info.get("ticker")
        name = stock_info.get("name")
        is_buying = stock_info.get("is_buying")
        shares = stock_info.get("shares")
        price = stock_info.get("price")
        change = stock_info.get("change")

        new_stock = Stock(ticker=symbol, name=name, shares=shares, price=price, change=change)
        new_stock.save()
        return HttpResponse(json.dumps({"message": "success"}))

    # Fetch details about a company and display it to the user
    profile = api.get_company_profile(ticker) # returns a list of dicts
    history = api.get_stock_history(ticker)  # returns a dict with symbol and historical list
    return render(request, "stockapp/detail.html",
        {"profile": profile[0], "history": history["historical"]}
    )

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

    return render(request, "stockapp/portfolio.html",
        {"balance": request.session["balance"], "stocks": Stock.objects.all()}
    )
