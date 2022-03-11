from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from stockapp.models import Portfolio, Stock
from .utils import USERNAME, PASSWORD


class PriceViewTests(TestCase):
    def setUp(self):
        # Initialize the balance to $10,000 before each test
        self.user = get_user_model().objects.create_user(
            username=USERNAME, password=PASSWORD)

    def test_redirect_without_login(self):
        # Check that the view redirects to the login screen if the user isn't logged in
        response = self.client.get(reverse("stockapp:price", args=("PRU",)))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, f"{reverse('login')}?next={reverse('stockapp:price', args=('PRU',))}")

    def test_view_renders(self):
        # Check that the JSON is populated with the correct information
        ticker = "PRU"
        old_stock = Stock.objects.create(ticker=ticker, name="Prudential Financial, Inc.",
                                         price=25.00, change=-1.12)
        old_portfolio = Portfolio.objects.create(
            user=self.user, stock=old_stock, shares=10)

        self.client.login(username=USERNAME, password=PASSWORD)
        response = self.client.get(reverse("stockapp:price", args=(ticker,)))

        self.assertEqual(response.status_code, 200)

        # Fetch the current stock price and change since they were updated in the GET request
        new_stock = Stock.objects.get(ticker=ticker)
        self.assertJSONEqual(response.content, {
            "price": float(new_stock.price),  # convert from Decimal to float
            "change": new_stock.change,
            "shares": old_portfolio.shares  # the porfolio shouldn't have changed
        })

    def test_is_case_insensitive(self):
        # Check that JSON is correct even if the ticker isn't in all caps
        ticker = "pRu"
        old_stock = Stock.objects.create(ticker=ticker.upper(), name="Prudential Financial, Inc.",
                                         price=25.00, change=-1.12)
        old_portfolio = Portfolio.objects.create(
            user=self.user, stock=old_stock, shares=10)

        self.client.login(username=USERNAME, password=PASSWORD)
        response = self.client.get(reverse("stockapp:price", args=(ticker,)))

        self.assertEqual(response.status_code, 200)

        # Fetch the current stock price and change since they were updated in the GET request
        new_stock = Stock.objects.get(ticker=ticker.upper())
        self.assertJSONEqual(response.content, {
            "price": float(new_stock.price),
            "change": new_stock.change,
            "shares": old_portfolio.shares  # the porfolio shouldn't have changed
        })

    def test_nonexistent_stock(self):
        # Check that the correct error shows when a stock isn't present in the user's porfolio
        self.client.login(username=USERNAME, password=PASSWORD)
        ticker = "PRU"
        response = self.client.get(reverse("stockapp:price", args=(ticker,)))

        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {
            "error": f"{ticker} doesn't exist in the user's porfolio"
        })

    def test_invalid_stock(self):
        # Check that the correct error shows if an invalid stock ticker is in the user's porfolio
        ticker = "qjxz"
        old_stock = Stock.objects.create(ticker=ticker.upper(), name="Blah Blah Inc.",
                                         price=0.00, change=0)
        Portfolio.objects.create(user=self.user, stock=old_stock, shares=100)

        self.client.login(username=USERNAME, password=PASSWORD)
        response = self.client.get(reverse("stockapp:price", args=(ticker,)))

        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {
            "error": f"No stock {ticker.upper()} found"
        })
