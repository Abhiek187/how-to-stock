from django.shortcuts import render
from django.views import generic

from .models import Stocks


class IndexView(generic.ListView):
    model = Stocks
    template_name = "stockapp/index.html"
    # context_object_name = 'people'

    # def get_queryset(self):
    #     """
    #     Return all the people in the database
    #     """
    #     return Person.objects.order_by('name')

class ScreenerView(generic.ListView):
    model = Stocks
    template_name = "stockapp/screener.html"
    # context_object_name = 'people'

    # def get_queryset(self):
    #     """
    #     Return all the people in the database
    #     """
    #     return Person.objects.order_by('name')

class FlashCardsView(generic.ListView):
    model = Stocks
    template_name = "stockapp/flashcards.html"
    # context_object_name = 'people'

    # def get_queryset(self):
    #     """
    #     Return all the people in the database
    #     """
    #     return Person.objects.order_by('name')

class PortfolioView(generic.ListView):
    model = Stocks
    template_name = "stockapp/portfolio.html"
    # context_object_name = 'people'

    # def get_queryset(self):
    #     """
    #     Return all the people in the database
    #     """
    #     return Person.objects.order_by('name')
