from django.shortcuts import render
from django.views import generic

from .models import Card, Stock


class IndexView(generic.ListView):
    model = Stock
    template_name = "stockapp/index.html"

class ScreenerView(generic.ListView):
    model = Stock
    template_name = "stockapp/screener.html"

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
