from django.urls import path

from . import views

app_name = "stockapp"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("screener", views.ScreenerView.as_view(), name="screener"),
    path("flashcards", views.FlashCardsView.as_view(), name="flashcards"),
    path("portfolio", views.PortfolioView.as_view(), name="portfolio")
]
