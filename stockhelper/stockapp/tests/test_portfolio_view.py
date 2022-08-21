from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from stockapp.models import Portfolio, Stock
from utils_test import USERNAME, PASSWORD


class PortfolioViewTests(TestCase):
    # Load all the card data
    fixtures = ["cards.json"]

    def setUp(self):
        # Create a user that can login to the view
        self.user = get_user_model().objects.create_user(
            username=USERNAME, password=PASSWORD)

    def test_redirect_without_login(self):
        # Check that the view redirects to the login screen if the user isn't logged in
        response = self.client.get(reverse("stockapp:portfolio"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, f"{reverse('login')}?next={reverse('stockapp:portfolio')}")

    def test_view_renders(self):
        # Check that the view renders properly
        self.client.login(username=USERNAME, password=PASSWORD)
        response = self.client.get(reverse("stockapp:portfolio"))
        self.assertEqual(response.status_code, 200)
        # Check that the title is correct
        self.assertContains(
            response, "<title>Portfolio | How to Stock</title>")
        self.assertContains(response, USERNAME)
        # Check that the relevant content on the portfolio page is present
        self.assertContains(response, "alert-info")
        self.assertContains(response, "Balance")
        self.assertContains(response, "Net Worth")
        self.assertContains(response, "net-worth-spinner")
        self.assertContains(response, "Nothing yet...start investing!")
        # Check that the correct context data is passed
        self.assertEqual(response.context["balance"], self.user.balance)
        self.assertQuerysetEqual(response.context["portfolios"], [])
        self.assertEqual({"portfolio", "roi", "sharePrice"},
                         response.context["terms"].keys())

    def test_stocks_show(self):
        # Check that the following Stock and Profile objects are rendered as a table
        stock1 = Stock.objects.create(ticker="FB", name="Facebook Inc",
                                      price=300.00, change=-3.43)
        portfolio1 = Portfolio.objects.create(
            user=self.user, stock=stock1, shares=5)
        stock2 = Stock.objects.create(ticker="AMZN", name="Amazon.com Inc",
                                      price=3000.00, change=-35.91)
        portfolio2 = Portfolio.objects.create(
            user=self.user, stock=stock2, shares=1)
        stock3 = Stock.objects.create(ticker="GOOGL", name="Alphabet Inc",
                                      price=2000.00, change=-3.73)
        portfolio3 = Portfolio.objects.create(
            user=self.user, stock=stock3, shares=2)

        self.client.login(username=USERNAME, password=PASSWORD)
        response = self.client.get(reverse("stockapp:portfolio"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, stock1.ticker)
        self.assertContains(response, stock1.name)
        self.assertContains(response, portfolio1.shares)
        self.assertContains(response, stock2.ticker)
        self.assertContains(response, stock2.name)
        self.assertContains(response, portfolio2.shares)
        self.assertContains(response, stock3.ticker)
        self.assertContains(response, stock3.name)
        self.assertContains(response, portfolio3.shares)
        # The price and change should be loading in the background
        self.assertContains(response, "price-spinner")
        self.assertContains(response, "change-spinner")
        self.assertContains(response, "</table>")

        self.assertEqual(response.context["balance"], self.user.balance)

        portfolio_list = [
            str({
                "stock__ticker": stock1.ticker,
                "stock__name": stock1.name,
                "shares": portfolio1.shares
            }),
            str({
                "stock__ticker": stock2.ticker,
                "stock__name": stock2.name,
                "shares": portfolio2.shares
            }),
            str({
                "stock__ticker": stock3.ticker,
                "stock__name": stock3.name,
                "shares": portfolio3.shares
            })
        ]
        # Ignore the order of each list
        self.assertQuerysetEqual(
            response.context["portfolios"], portfolio_list, transform=repr, ordered=False)
