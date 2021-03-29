from django.test import TestCase
from django.urls import reverse

from .forms import ScreenerForm
from .models import Card, Stock
import json

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
        self.assertContains(response, "<title>How to Stock</title>")
        # Check that the navbar is present
        self.assertContains(response, "navbar")
        self.assertContains(response, "<a class=\"link-home nav-link active\" aria-current=\"page\"")
        # Check that the relevant content on the home page is present
        self.assertContains(response, "Welcome to How to Stock!")
        self.assertContains(response, "<strong>Home</strong>")
        self.assertContains(response, "<strong>Screener</strong>")
        self.assertContains(response, "<strong>Flashcards</strong>")
        self.assertContains(response, "<strong>Portfolio</strong>")
        self.assertContains(response, "Data provided by Financial Modeling Prep")
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
        self.assertContains(response, "<title>Screener</title>")
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
        # Initialize all the variables needed for most of the tests
        self.stock_purchase = {
            "ticker": "PRU",
            "name": "Prudential Financial Inc",
            "isBuying": True,
            "shares": 10,
            "price": 25.00,
            "change": -1.12
        }

        self.session = self.client.session
        self.session["balance"] = 10000
        self.session.save()

    def create_stock(self):
        # Don't alter self.stock_purchase
        p_copy = self.stock_purchase.copy()
        del p_copy["isBuying"] # isBuying isn't part of the Stock model
        return Stock.objects.create(**p_copy)

    def send_post_request(self):
        return self.client.post(reverse("stockapp:detail", args=("PRU",)),
            json.dumps(self.stock_purchase), content_type="application/json")

    def test_view_renders(self):
        # Check that the view renders properly
        response = self.client.get(reverse("stockapp:detail", args=("PRU",)))
        self.assertEqual(response.status_code, 200)
        # Check that the title is correct
        self.assertContains(response, "<title>Details - Prudential Financial Inc</title>")
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
        self.assertContains(response, "Transaction")
        self.assertContains(response, "Shares")
        self.assertContains(response, "New Balance:")
        self.assertContains(response, "toast")
        self.assertContains(response, "description")
        # Check that the correct context data is passed
        self.assertIsNotNone(response.context["profile"])
        self.assertIsNotNone(response.context["history"])
        self.assertEqual(response.context["balance"], self.session["balance"])
        self.assertEqual({
            "beta", "broker", "dividendYield", "marketCap", "marketExchange", "marketOrder", "risk",
            "sharePrice", "trader", "volatility", "volume"
        }, response.context["terms"].keys())

    def test_buy_new_stock(self):
        # Check that buying a stock with 0 shares creates a new Stock object
        response = self.send_post_request()

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"status": "success"})
        self.assertEqual(self.client.session["balance"],
            self.session["balance"] - self.stock_purchase["shares"] * self.stock_purchase["price"])
        self.assertQuerysetEqual(Stock.objects.all(), ["<Stock: PRU - Prudential Financial Inc>"])

    def test_sell_new_stock(self):
        # Check that selling a new stock returns an error
        self.stock_purchase["isBuying"] = False
        response = self.send_post_request()

        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {"status": "failure", "maxShares": 0})
        self.assertEqual(self.client.session["balance"], self.session["balance"])
        self.assertQuerysetEqual(Stock.objects.all(), [])

    def test_buy_more_stock(self):
        # Check that the number of shares increased after buying more shares of an existing stock
        old_stock = self.create_stock()
        response = self.send_post_request()

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"status": "success"})
        self.assertEqual(self.client.session["balance"],
            self.session["balance"] - self.stock_purchase["shares"] * self.stock_purchase["price"])
        new_stock = Stock.objects.get(pk="PRU")
        self.assertEqual(new_stock.shares, old_stock.shares + self.stock_purchase["shares"])

    def test_sell_some_stock(self):
        # Check that the number of shares decreased after selling some shares of an existing stock
        old_stock = self.create_stock()
        self.stock_purchase["isBuying"] = False
        self.stock_purchase["shares"] = 5
        response = self.send_post_request()

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"status": "success"})
        self.assertEqual(self.client.session["balance"],
            self.session["balance"] + self.stock_purchase["shares"] * self.stock_purchase["price"])
        new_stock = Stock.objects.get(pk="PRU")
        self.assertEqual(new_stock.shares, old_stock.shares - self.stock_purchase["shares"])

    def test_sell_all_stock(self):
        # Check that the Stock object is deleted after selling all the shares
        old_stock = self.create_stock()
        self.stock_purchase["isBuying"] = False
        self.stock_purchase["shares"] = 10
        response = self.send_post_request()

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"status": "success"})
        self.assertEqual(self.client.session["balance"],
            self.session["balance"] + self.stock_purchase["shares"] * self.stock_purchase["price"])
        self.assertQuerysetEqual(Stock.objects.all(), [])

    def test_sell_too_much_stock(self):
        # Check that selling too many stocks results in an error
        old_stock = self.create_stock()
        self.stock_purchase["isBuying"] = False
        self.stock_purchase["shares"] = 15
        response = self.send_post_request()

        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {"status": "failure", "maxShares": old_stock.shares})
        self.assertEqual(self.client.session["balance"], self.session["balance"])
        new_stock = Stock.objects.get(pk="PRU")
        self.assertEqual(new_stock.shares, old_stock.shares)

    def tearDown(self):
        # Remove the session variable after each test
        del self.session["balance"]


class FlashcardsViewTests(TestCase):
    def test_view_renders(self):
        # Check that the view renders properly
        response = self.client.get(reverse("stockapp:flashcards"))
        self.assertEqual(response.status_code, 200)
        # Check that the title is correct
        self.assertContains(response, "<title>Flashcards</title>")
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

    def test_view_renders(self):
        # Check that the view renders properly
        response = self.client.get(reverse("stockapp:portfolio"))
        session = self.client.session
        self.assertEqual(response.status_code, 200)
        # Check that the title is correct
        self.assertContains(response, "<title>Portfolio</title>")
        # Check that the relevant content on the portfolio page is present
        self.assertContains(response, "Balance")
        self.assertContains(response, "Net Worth")
        self.assertContains(response, "Nothing yet...start investing!")
        # Check that the correct context data is passed
        self.assertEqual(response.context["balance"], session["balance"])
        self.assertEqual(response.context["net_worth"], response.context["balance"])
        self.assertQuerysetEqual(response.context["stocks"], [])
        self.assertEqual({"portfolio", "roi", "sharePrice"}, response.context["terms"].keys())

    def test_stocks_show(self):
        # Check that the following Stock objects are rendered and the net worth changes
        old_stock1 = Stock.objects.create(ticker="FB", name="Facebook Inc", shares=5,
            price=300.00, change=-3.43)
        old_stock2 = Stock.objects.create(ticker="AMZN", name="Amazon.com Inc", shares=1,
            price=3000.00, change=-35.91)
        old_stock3 = Stock.objects.create(ticker="GOOGL", name="Alphabet Inc", shares=2,
            price=2000.00, change=-3.73)

        response = self.client.get(reverse("stockapp:portfolio"))
        session = self.client.session
        session["balance"] = 10000
        session.save()
        new_stock1 = Stock.objects.get(pk=old_stock1.ticker)
        new_stock2 = Stock.objects.get(pk=old_stock2.ticker)
        new_stock3 = Stock.objects.get(pk=old_stock3.ticker)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, old_stock1.ticker)
        self.assertContains(response, old_stock1.name)
        self.assertContains(response, old_stock1.shares)
        # Price and change should be up-to-date
        self.assertContains(response, new_stock1.price)
        self.assertContains(response, new_stock1.change)
        self.assertContains(response, old_stock2.ticker)
        self.assertContains(response, old_stock2.name)
        self.assertContains(response, old_stock2.shares)
        self.assertContains(response, new_stock2.price)
        self.assertContains(response, new_stock2.change)
        self.assertContains(response, old_stock3.ticker)
        self.assertContains(response, old_stock3.name)
        self.assertContains(response, old_stock3.shares)
        self.assertContains(response, new_stock3.price)
        self.assertContains(response, new_stock3.change)
        self.assertContains(response, "</table>")
        self.assertEqual(response.context["balance"], session["balance"])
        net_worth = (session["balance"] + old_stock1.shares * new_stock1.price + old_stock2.shares
            * new_stock2.price + old_stock3.shares * new_stock3.price)
        # Convert the Decimal to a float
        self.assertAlmostEqual(response.context["net_worth"], float(net_worth))
        stock_list = [
            f"<Stock: {new_stock1.ticker} - {new_stock1.name}>",
            f"<Stock: {new_stock2.ticker} - {new_stock2.name}>",
            f"<Stock: {new_stock3.ticker} - {new_stock3.name}>"
        ]
        # Ignore the order of each list
        self.assertQuerysetEqual(response.context["stocks"], stock_list, ordered=False)


class BalanceViewTests(TestCase):
    def test_view_renders(self):
        # Check that the view renders properly
        response = self.client.get(reverse("stockapp:balance"))
        session = self.client.session
        self.assertEqual(response.status_code, 200)
        # Check that the relevant content on the balance page is present
        self.assertContains(response, session.get("balance", 10000))
