from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from stockapp.models import Portfolio, Stock, User
import json
from utils_test import USERNAME, PASSWORD


class DetailViewTests(TestCase):
    # Load all the card data
    fixtures = ["cards.json"]

    def setUp(self):
        # Create a user that can login to the view
        self.user = get_user_model().objects.create_user(
            username=USERNAME, password=PASSWORD)

        # Initialize all the variables needed for most of the tests
        self.stock_purchase = {
            "user": self.user,
            "ticker": "PRU",
            "name": "Prudential Financial, Inc.",
            "isBuying": True,
            "shares": 10,
            "price": 25.00,
            "change": -1.12
        }

        stock_keys = ["ticker", "name", "price", "change"]
        stock_dict = {k: self.stock_purchase[k]
                      for k in self.stock_purchase.keys() if k in stock_keys}
        self.test_stock = Stock.objects.create(**stock_dict)

    def create_portfolio(self):
        # Only keep the fields in self.stock_purchase that are Portfolio model
        return Portfolio.objects.create(user=self.stock_purchase["user"], stock=self.test_stock,
                                        shares=self.stock_purchase["shares"])

    def send_post_request(self):
        p_copy = self.stock_purchase.copy()
        del p_copy["user"]  # user isn't serializable
        return self.client.post(reverse("stockapp:detail", args=("PRU",)),
                                json.dumps(p_copy), content_type="application/json")

    def test_redirect_without_login(self):
        # Check that the view redirects to the login screen if the user isn't logged in
        response = self.client.get(reverse("stockapp:detail", args=("PRU",)))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, f"{reverse('login')}?next={reverse('stockapp:detail', args=('PRU',))}")

    def test_view_renders(self):
        # Check that the view renders properly
        self.client.login(username=USERNAME, password=PASSWORD)
        response = self.client.get(reverse("stockapp:detail", args=("JPM",)))
        self.assertEqual(response.status_code, 200)
        # Check that the title is correct
        # Need to do two separate checks due to the added newlines from jinja tags
        self.assertContains(response, "Details - JPMorgan Chase &amp; Co.")
        self.assertContains(response, " | How to Stock")
        self.assertContains(response, USERNAME)
        # Check that the relevant content on the details page is present
        self.assertContains(response, "history-data")
        self.assertContains(response, "JPM")
        self.assertContains(response, "short-chart")
        self.assertContains(response, "short-predict")
        self.assertContains(response, "short-mean")
        self.assertContains(response, "Beta:")
        self.assertContains(response, "long-chart")
        self.assertContains(response, "long-predict")
        self.assertContains(response, "long-mean")
        self.assertContains(response, "market order")
        self.assertContains(response, "Transaction")
        self.assertContains(response, "Shares")
        self.assertContains(response, "New Balance:")
        self.assertContains(response, "toast")
        self.assertContains(response, "description")
        # Check that the correct context data is passed
        self.assertIsNotNone(response.context["profile"])
        self.assertIsNotNone(response.context["history"])
        self.assertEqual(response.context["balance"], self.user.balance)
        self.assertEqual({
            "beta", "broker", "dividendYield", "marketCap", "marketExchange", "marketOrder", "risk",
            "trader", "volatility", "volume"
        }, response.context["terms"].keys())

    def test_invalid_stock(self):
        # Check that an error message shows if the ticker is invalid
        self.client.login(username=USERNAME, password=PASSWORD)
        bad_ticker = "qjxz"
        response = self.client.get(
            reverse("stockapp:detail", args=(bad_ticker,)))

        self.assertEqual(response.status_code, 400)
        self.assertContains(response, "Details - ???", status_code=400)
        self.assertContains(
            response, f"Error: Unknown stock ticker: {bad_ticker}", status_code=400)
        self.assertIsNone(response.context["profile"])
        self.assertEqual(response.context["history"], bad_ticker)

    def test_buy_new_stock(self):
        # Check that buying a stock with 0 shares creates a new Stock object
        self.client.login(username=USERNAME, password=PASSWORD)
        porfolio = self.create_portfolio()
        response = self.send_post_request()

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"status": "success"})
        self.assertEqual(User.objects.get(username=USERNAME).balance,
                         self.user.balance - self.stock_purchase["shares"] * self.stock_purchase["price"])
        self.assertQuerySetEqual(Stock.objects.all(), [self.test_stock])
        self.assertQuerySetEqual(Portfolio.objects.all(), [porfolio])

    def test_sell_new_stock(self):
        # Check that selling a new stock returns an error
        self.client.login(username=USERNAME, password=PASSWORD)
        self.stock_purchase["isBuying"] = False
        response = self.send_post_request()

        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {
                             "status": "failure", "maxShares": 0})
        self.assertEqual(User.objects.get(
            username=USERNAME).balance, self.user.balance)
        self.assertQuerySetEqual(Stock.objects.all(), [self.test_stock])
        self.assertQuerySetEqual(Portfolio.objects.all(), [])

    def test_buy_more_stock(self):
        # Check that the number of shares increased after buying more shares of an existing stock
        self.client.login(username=USERNAME, password=PASSWORD)
        old_portfolio = self.create_portfolio()
        response = self.send_post_request()

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"status": "success"})
        self.assertEqual(User.objects.get(username=USERNAME).balance, self.user.balance -
                         self.stock_purchase["shares"] * self.stock_purchase["price"])
        self.assertQuerySetEqual(Stock.objects.all(), [self.test_stock])
        new_portfolio = Portfolio.objects.get(
            user=self.user, stock=self.test_stock)
        self.assertEqual(new_portfolio.shares, old_portfolio.shares +
                         self.stock_purchase["shares"])

    def test_sell_some_stock(self):
        # Check that the number of shares decreased after selling some shares of an existing stock
        self.client.login(username=USERNAME, password=PASSWORD)
        old_portfolio = self.create_portfolio()
        self.stock_purchase["isBuying"] = False
        self.stock_purchase["shares"] = 5
        response = self.send_post_request()

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"status": "success"})
        self.assertEqual(User.objects.get(username=USERNAME).balance, self.user.balance +
                         self.stock_purchase["shares"] * self.stock_purchase["price"])
        self.assertQuerySetEqual(Stock.objects.all(), [self.test_stock])
        new_portfolio = Portfolio.objects.get(
            user=self.user, stock=self.test_stock)
        self.assertEqual(new_portfolio.shares, old_portfolio.shares -
                         self.stock_purchase["shares"])

    def test_sell_all_stock(self):
        # Check that the Stock object is deleted after selling all the shares
        self.client.login(username=USERNAME, password=PASSWORD)
        self.create_portfolio()
        self.stock_purchase["isBuying"] = False
        self.stock_purchase["shares"] = 10
        response = self.send_post_request()

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"status": "success"})
        self.assertEqual(User.objects.get(username=USERNAME).balance, self.user.balance +
                         self.stock_purchase["shares"] * self.stock_purchase["price"])
        self.assertQuerySetEqual(Stock.objects.all(), [self.test_stock])
        self.assertQuerySetEqual(Portfolio.objects.all(), [])

    def test_sell_too_much_stock(self):
        # Check that selling too many stocks results in an error
        self.client.login(username=USERNAME, password=PASSWORD)
        old_portfolio = self.create_portfolio()
        self.stock_purchase["isBuying"] = False
        self.stock_purchase["shares"] = 15
        response = self.send_post_request()

        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {
                             "status": "failure", "maxShares": old_portfolio.shares})
        self.assertEqual(User.objects.get(
            username=USERNAME).balance, self.user.balance)
        self.assertQuerySetEqual(Stock.objects.all(), [self.test_stock])
        new_portfolio = Portfolio.objects.get(
            user=self.user, stock=self.test_stock)
        self.assertEqual(new_portfolio.shares, old_portfolio.shares)
