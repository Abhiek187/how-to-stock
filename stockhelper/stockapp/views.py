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
            ticker_list = get_stock_data(form.cleaned_data)
            print(ticker_list)
            # Return an HttpResponseRedirect to prevent the data from being posted twice
            return HttpResponseRedirect(reverse("stockapp:screener"))
    else:
        # Show an empty form when entering the screener page
        form = ScreenerForm()

    return render(request, "stockapp/screener.html", {"form": form})

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
