from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import generic

from .api import get_stock_data
from .forms import ScreenerForm
from .models import Card, Stock

class IndexView(generic.ListView):
    model = Stock
    template_name = "stockapp/index.html"

def get_stocks(request):
    if request.method == "POST":
        # Keep the form as is after submitting
        form = ScreenerForm(request.POST)

        if form.is_valid() and form.is_bound:
            # Query the dataset
            stock_data = get_stock_data(form.cleaned_data)
            request.session["results"] = stock_data
            # Return an HttpResponseRedirect to prevent the data from being posted twice
            return HttpResponseRedirect(reverse("stockapp:screener"))

    # Show an empty form when entering the screener page
    form = ScreenerForm()
    # Display the results after a POST request
    results = request.session.get("results")  # results will be None if there aren't any results
    request.session.pop("results", None)  # don't throw an error if the key isn't present
    return render(request, "stockapp/screener.html", {"form": form, "results": results})

class FlashCardsView(generic.ListView):
    model = Card
    template_name = "stockapp/flashcards.html"
    context_object_name = "cards"

    def get_queryset(self):
        """
        Sort the cards alphabetically
        """
        return Card.objects.order_by("word")

class PortfolioView(generic.ListView):
    model = Stock
    template_name = "stockapp/portfolio.html"
