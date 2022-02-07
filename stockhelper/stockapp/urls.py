from django.urls import path

from . import views

app_name = "stockapp"
urlpatterns = [
    path("", views.get_index, name="index"),
    path("screener", views.get_stocks, name="screener"),
    path("details/<ticker>", views.get_stock_details, name="detail"),
    path("flashcards", views.FlashCardsView.as_view(), name="flashcards"),
    path("portfolio", views.get_portfolio, name="portfolio"),
    path("session/balance", views.SessionBalanceView.as_view(), name="balance"),
    path("api/price/<ticker>", views.PriceView.as_view(), name="price")
]
