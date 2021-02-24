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
