from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .forms import ScreenerForm
from .models import Card, Stock, User
import json

USERNAME = "foo"
PASSWORD = "bar"


# Create tests for each view
class HomeViewTests(TestCase):
    # Load all the card data
    fixtures = ["cards.json"]

    # All test functions must start with test*
    def test_view_renders(self):
        # Check that the view renders properly
        response = self.client.get(reverse("stockapp:index"))
        self.assertEqual(response.status_code, 200)
        # Check that the title is correct
        self.assertContains(response, "<title>Home | How to Stock</title>")
        # Check that the navbar is present
        self.assertContains(response, "navbar")
        self.assertContains(
            response, "<a class=\"link-home nav-link active\" aria-current=\"page\"")
        # Check that the relevant content on the home page is present
        self.assertContains(response, "Welcome to How to Stock!")
        self.assertContains(response, "<strong>Home</strong>")
        self.assertContains(response, "<strong>Screener</strong>")
        self.assertContains(response, "<strong>Flashcards</strong>")
        self.assertContains(response, "<strong>Portfolio</strong>")
        self.assertContains(
            response, "Data provided by Financial Modeling Prep")
        # Check that the correct context data is passed
        self.assertIn("equity", response.context["terms"])


class ScreenerViewTests(TestCase):
    # Load all the card data
    fixtures = ["cards.json"]

    def test_view_renders(self):
        # Check that the view renders properly
        response = self.client.get(reverse("stockapp:screener"))
        self.assertEqual(response.status_code, 200)
        # Check that the title is correct
        self.assertContains(response, "<title>Screener | How to Stock</title>")
        # Check that the relevant content on the screener page is present
        self.assertContains(response, "</form>")
        self.assertContains(response, "Results will show up here...")
        # Check that the correct context data is passed
        self.assertIsNotNone(response.context["form"])
        self.assertEqual(response.context["results"], None)
        self.assertEqual({
            "beta", "dividendYield", "etf", "index", "indexFund", "marketCap", "marketExchange",
            "mutualFund", "sharePrice", "volume"
        }, response.context["terms"].keys())

    def test_post_form(self):
        # Check that submitting the form produces results
        form_data = {
            "country": "US",
            "price_relation": ">",
            "price_value": 1000,
            "sector": "Any",
            "exchange": "nasdaq"
        }
        form = ScreenerForm(form_data)
        self.assertTrue(form.is_valid())
        self.assertTrue(form.is_bound)

        response = self.client.post(reverse("stockapp:screener"), form_data,
                                    content_type="application/json")
        # Check that the POST request redirects to a successful GET request
        self.assertEqual(response.status_code, 200)


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

    def create_stock(self):
        # Don't alter self.stock_purchase
        p_copy = self.stock_purchase.copy()
        del p_copy["isBuying"]  # isBuying isn't part of the Stock model
        return Stock.objects.create(**p_copy)

    def send_post_request(self):
        p_copy = self.stock_purchase.copy()
        del p_copy["user"]  # user isn't serializable
        return self.client.post(reverse("stockapp:detail", args=("PRU",)),
                                json.dumps(p_copy), content_type="application/json")

    def test_redirect_without_login(self):
        # Check that the view redirects to the login screen if the user isn't logged in
        response = self.client.get(reverse("stockapp:detail", args=("Pru",)))
        self.assertEqual(response.status_code, 302)

    def test_view_renders(self):
        # Check that the view renders properly
        self.client.login(username=USERNAME, password=PASSWORD)
        response = self.client.get(reverse("stockapp:detail", args=("PRU",)))
        self.assertEqual(response.status_code, 200)
        # Check that the title is correct
        self.assertContains(
            response, "<title>Details - Prudential Financial, Inc. | How to Stock</title>")
        # Check that the relevant content on the details page is present
        self.assertContains(response, "history-data")
        self.assertContains(response, "PRU")
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

    def test_buy_new_stock(self):
        # Check that buying a stock with 0 shares creates a new Stock object
        self.client.login(username=USERNAME, password=PASSWORD)
        response = self.send_post_request()

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"status": "success"})
        self.assertEqual(User.objects.get(username=USERNAME).balance,
                         self.user.balance - self.stock_purchase["shares"] * self.stock_purchase["price"])
        self.assertQuerysetEqual(Stock.objects.all(), [
                                 f"<Stock: {USERNAME}: {self.stock_purchase['ticker']} - {self.stock_purchase['name']}>"])

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
        self.assertQuerysetEqual(Stock.objects.all(), [])

    def test_buy_more_stock(self):
        # Check that the number of shares increased after buying more shares of an existing stock
        self.client.login(username=USERNAME, password=PASSWORD)
        old_stock = self.create_stock()
        response = self.send_post_request()

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"status": "success"})
        self.assertEqual(User.objects.get(username=USERNAME).balance, self.user.balance -
                         self.stock_purchase["shares"] * self.stock_purchase["price"])
        new_stock = Stock.objects.get(user=self.user, ticker="PRU")
        self.assertEqual(new_stock.shares, old_stock.shares +
                         self.stock_purchase["shares"])

    def test_sell_some_stock(self):
        # Check that the number of shares decreased after selling some shares of an existing stock
        self.client.login(username=USERNAME, password=PASSWORD)
        old_stock = self.create_stock()
        self.stock_purchase["isBuying"] = False
        self.stock_purchase["shares"] = 5
        response = self.send_post_request()

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"status": "success"})
        self.assertEqual(User.objects.get(username=USERNAME).balance, self.user.balance +
                         self.stock_purchase["shares"] * self.stock_purchase["price"])
        new_stock = Stock.objects.get(user=self.user, ticker="PRU")
        self.assertEqual(new_stock.shares, old_stock.shares -
                         self.stock_purchase["shares"])

    def test_sell_all_stock(self):
        # Check that the Stock object is deleted after selling all the shares
        self.client.login(username=USERNAME, password=PASSWORD)
        self.create_stock()
        self.stock_purchase["isBuying"] = False
        self.stock_purchase["shares"] = 10
        response = self.send_post_request()

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"status": "success"})
        self.assertEqual(User.objects.get(username=USERNAME).balance, self.user.balance +
                         self.stock_purchase["shares"] * self.stock_purchase["price"])
        self.assertQuerysetEqual(Stock.objects.all(), [])

    def test_sell_too_much_stock(self):
        # Check that selling too many stocks results in an error
        self.client.login(username=USERNAME, password=PASSWORD)
        old_stock = self.create_stock()
        self.stock_purchase["isBuying"] = False
        self.stock_purchase["shares"] = 15
        response = self.send_post_request()

        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {
                             "status": "failure", "maxShares": old_stock.shares})
        self.assertEqual(User.objects.get(
            username=USERNAME).balance, self.user.balance)
        new_stock = Stock.objects.get(user=self.user, ticker="PRU")
        self.assertEqual(new_stock.shares, old_stock.shares)


class FlashcardsViewTests(TestCase):
    def test_view_renders(self):
        # Check that the view renders properly
        response = self.client.get(reverse("stockapp:flashcards"))
        self.assertEqual(response.status_code, 200)
        # Check that the title is correct
        self.assertContains(
            response, "<title>Flashcards | How to Stock</title>")
        # Check that the relevant content on the flashcards page is present
        self.assertContains(response, "description")
        # Check that the correct context data is passed
        self.assertQuerysetEqual(response.context["cards"], [])

    def test_sample_cards(self):
        # Check that the following Card objects are rendered
        card1 = Card.objects.create(word="Money",
                                    definition="The currency required to make purchases")
        card2 = Card.objects.create(word="Bank",
                                    definition="The place where you deposit or withdraw money")
        response = self.client.get(reverse("stockapp:flashcards"))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, card1.id)
        self.assertContains(response, card1.word)
        self.assertContains(response, card1.definition)
        self.assertNotContains(response, card2.id)
        self.assertContains(response, card2.word)
        self.assertContains(response, card2.definition)


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

    def test_view_renders(self):
        # Check that the view renders properly
        self.client.login(username=USERNAME, password=PASSWORD)
        response = self.client.get(reverse("stockapp:portfolio"))
        self.assertEqual(response.status_code, 200)
        # Check that the title is correct
        self.assertContains(
            response, "<title>Portfolio | How to Stock</title>")
        # Check that the relevant content on the portfolio page is present
        self.assertContains(response, "alert-info")
        self.assertContains(response, "Balance")
        self.assertContains(response, "Net Worth")
        self.assertContains(response, "net-worth-spinner")
        self.assertContains(response, "Nothing yet...start investing!")
        # Check that the correct context data is passed
        self.assertEqual(response.context["balance"], self.user.balance)
        self.assertQuerysetEqual(response.context["stocks"], [])
        self.assertEqual({"portfolio", "roi", "sharePrice"},
                         response.context["terms"].keys())

    def test_stocks_show(self):
        # Check that the following Stock objects are rendered as a table
        stock1 = Stock.objects.create(user=self.user, ticker="FB", name="Facebook Inc", shares=5,
                                      price=300.00, change=-3.43)
        stock2 = Stock.objects.create(user=self.user, ticker="AMZN", name="Amazon.com Inc", shares=1,
                                      price=3000.00, change=-35.91)
        stock3 = Stock.objects.create(user=self.user, ticker="GOOGL", name="Alphabet Inc", shares=2,
                                      price=2000.00, change=-3.73)

        self.client.login(username=USERNAME, password=PASSWORD)
        response = self.client.get(reverse("stockapp:portfolio"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, stock1.ticker)
        self.assertContains(response, stock1.name)
        self.assertContains(response, stock1.shares)
        self.assertContains(response, stock2.ticker)
        self.assertContains(response, stock2.name)
        self.assertContains(response, stock2.shares)
        self.assertContains(response, stock3.ticker)
        self.assertContains(response, stock3.name)
        self.assertContains(response, stock3.shares)
        # The price and change should be loading in the background
        self.assertContains(response, "price-spinner")
        self.assertContains(response, "change-spinner")
        self.assertContains(response, "</table>")

        self.assertEqual(response.context["balance"], self.user.balance)
        stock_list = [
            f"<Stock: {USERNAME}: {stock1.ticker} - {stock1.name}>",
            f"<Stock: {USERNAME}: {stock2.ticker} - {stock2.name}>",
            f"<Stock: {USERNAME}: {stock3.ticker} - {stock3.name}>"
        ]
        # Ignore the order of each list
        self.assertQuerysetEqual(
            response.context["stocks"], stock_list, ordered=False)


class BalanceViewTests(TestCase):
    def setUp(self):
        # Initialize the balance to $10,000 before each test
        self.user = get_user_model().objects.create_user(
            username=USERNAME, password=PASSWORD)

    def test_redirect_without_login(self):
        # Check that the view redirects to the login screen if the user isn't logged in
        response = self.client.get(reverse("stockapp:balance"))
        self.assertEqual(response.status_code, 302)

    def test_view_renders(self):
        # Check that the view renders properly
        self.client.login(username=USERNAME, password=PASSWORD)
        response = self.client.get(reverse("stockapp:balance"))
        self.assertEqual(response.status_code, 200)
        # Check that the relevant content on the balance page is present
        self.assertContains(response, self.user.balance)


class PricesViewTests(TestCase):
    def setUp(self):
        # Initialize the balance to $10,000 before each test
        self.user = get_user_model().objects.create_user(
            username=USERNAME, password=PASSWORD)

    def test_redirect_without_login(self):
        # Check that the view redirects to the login screen if the user isn't logged in
        response = self.client.get(reverse("stockapp:prices"))
        self.assertEqual(response.status_code, 302)

    def test_view_renders(self):
        # Check that the view renders properly
        self.client.login(username=USERNAME, password=PASSWORD)
        response = self.client.get(reverse("stockapp:prices"))
        self.assertEqual(response.status_code, 200)
        # Check that the relevant content on the prices page is present
        self.assertJSONEqual(response.content, {
                             "netWorth": f"{self.user.balance:.2f}", "prices": []})

    def test_stocks_show(self):
        # Check that the stock data defined below is present in the output
        old_stock1 = Stock.objects.create(user=self.user, ticker="FB", name="Facebook Inc", shares=5,
                                          price=300.00, change=-3.43)
        old_stock2 = Stock.objects.create(user=self.user, ticker="AMZN", name="Amazon.com Inc", shares=1,
                                          price=3000.00, change=-35.91)
        old_stock3 = Stock.objects.create(user=self.user, ticker="GOOGL", name="Alphabet Inc", shares=2,
                                          price=2000.00, change=-3.73)

        self.client.login(username=USERNAME, password=PASSWORD)
        response = self.client.get(reverse("stockapp:prices"))
        new_stock1 = Stock.objects.get(
            user=self.user, ticker=old_stock1.ticker)
        new_stock2 = Stock.objects.get(
            user=self.user, ticker=old_stock2.ticker)
        new_stock3 = Stock.objects.get(
            user=self.user, ticker=old_stock3.ticker)

        self.assertEqual(response.status_code, 200)
        net_worth = (self.user.balance + old_stock1.shares * new_stock1.price
                     + old_stock2.shares * new_stock2.price + old_stock3.shares * new_stock3.price)
        # Convert the Decimals to strings
        prices = [
            {"price": str(new_stock1.price), "change": new_stock1.change},
            {"price": str(new_stock2.price), "change": new_stock2.change},
            {"price": str(new_stock3.price), "change": new_stock3.change}
        ]

        resp = json.loads(response.content)
        # Account for floating point errors by 7 decimal places
        self.assertAlmostEqual(float(resp["netWorth"]), float(net_worth))
        self.assertEqual(resp["prices"], prices)
