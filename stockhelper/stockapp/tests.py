from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .forms import ScreenerForm
from .models import Card, Portfolio, Stock, User
import json
from stockhelper.forms import CustomUserCreationForm

USERNAME = "testuser"
PASSWORD = "howtostock"


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
        self.assertContains(response, "Login")
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

    def test_root_view_redirects(self):
        # Check that the root view redirects to the home view
        response = self.client.get("/")
        self.assertEqual(response.status_code, 301)
        self.assertRedirects(response, reverse(
            "stockapp:index"), status_code=301)


class ScreenerViewTests(TestCase):
    # Load all the card data
    fixtures = ["cards.json"]

    def test_view_renders(self):
        # Check that the view renders properly
        response = self.client.get(reverse("stockapp:screener"))
        self.assertEqual(response.status_code, 200)
        # Check that the title is correct
        self.assertContains(response, "<title>Screener | How to Stock</title>")
        self.assertContains(response, "Login")
        # Check that the relevant content on the screener page is present
        self.assertContains(response, "</form>")
        self.assertContains(response, "Results will show up here...")
        # Check that the correct context data is passed
        self.assertIsInstance(response.context["form"], ScreenerForm)
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

        response = self.client.post(reverse("stockapp:screener"), form_data)
        # Check that the POST request redirects to the screener page
        self.assertEqual(response.status_code, 302)
        self.assertIn("results", self.client.session)
        self.assertRedirects(response, reverse("stockapp:screener"))


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
        response = self.client.get(reverse("stockapp:detail", args=("PRU",)))
        self.assertEqual(response.status_code, 200)
        # Check that the title is correct
        # Need to do two separate checks due to the added newlines from jinja tags
        self.assertContains(response, "Details - Prudential Financial, Inc.")
        self.assertContains(response, " | How to Stock")
        self.assertContains(response, USERNAME)
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

    def test_invalid_stock(self):
        # Check that an error message shows if the ticker is invalid
        self.client.login(username=USERNAME, password=PASSWORD)
        bad_ticker = "qjxz"
        response = self.client.get(
            reverse("stockapp:detail", args=(bad_ticker,)))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Details - ???")
        self.assertContains(
            response, f"Error: Unknown stock ticker: {bad_ticker}")
        self.assertIsNone(response.context["profile"])
        self.assertEqual(response.context["history"], bad_ticker)

    def test_buy_new_stock(self):
        # Check that buying a stock with 0 shares creates a new Stock object
        self.client.login(username=USERNAME, password=PASSWORD)
        response = self.send_post_request()

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"status": "success"})
        self.assertEqual(User.objects.get(username=USERNAME).balance,
                         self.user.balance - self.stock_purchase["shares"] * self.stock_purchase["price"])
        self.assertQuerysetEqual(Stock.objects.all(), [
                                 f"<Stock: {self.stock_purchase['ticker']} - {self.stock_purchase['name']}>"])
        self.assertQuerysetEqual(Portfolio.objects.all(), [
                                 f"<Portfolio: {USERNAME}: {self.stock_purchase['shares']} shares of {self.test_stock}>"])

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
        self.assertQuerysetEqual(Stock.objects.all(), [
                                 f"<Stock: {self.stock_purchase['ticker']} - {self.stock_purchase['name']}>"])
        self.assertQuerysetEqual(Portfolio.objects.all(), [])

    def test_buy_more_stock(self):
        # Check that the number of shares increased after buying more shares of an existing stock
        self.client.login(username=USERNAME, password=PASSWORD)
        old_portfolio = self.create_portfolio()
        response = self.send_post_request()

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"status": "success"})
        self.assertEqual(User.objects.get(username=USERNAME).balance, self.user.balance -
                         self.stock_purchase["shares"] * self.stock_purchase["price"])
        self.assertQuerysetEqual(Stock.objects.all(), [
                                 f"<Stock: {self.stock_purchase['ticker']} - {self.stock_purchase['name']}>"])
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
        self.assertQuerysetEqual(Stock.objects.all(), [
                                 f"<Stock: {self.stock_purchase['ticker']} - {self.stock_purchase['name']}>"])
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
        self.assertQuerysetEqual(Stock.objects.all(), [
                                 f"<Stock: {self.stock_purchase['ticker']} - {self.stock_purchase['name']}>"])
        self.assertQuerysetEqual(Portfolio.objects.all(), [])

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
        self.assertQuerysetEqual(Stock.objects.all(), [
                                 f"<Stock: {self.stock_purchase['ticker']} - {self.stock_purchase['name']}>"])
        new_portfolio = Portfolio.objects.get(
            user=self.user, stock=self.test_stock)
        self.assertEqual(new_portfolio.shares, old_portfolio.shares)


class FlashcardsViewTests(TestCase):
    def test_view_renders(self):
        # Check that the view renders properly
        response = self.client.get(reverse("stockapp:flashcards"))
        self.assertEqual(response.status_code, 200)
        # Check that the title is correct
        self.assertContains(
            response, "<title>Flashcards | How to Stock</title>")
        self.assertContains(response, "Login")
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
            response.context["portfolios"], portfolio_list, ordered=False)


class BalanceViewTests(TestCase):
    def setUp(self):
        # Initialize the balance to $10,000 before each test
        self.user = get_user_model().objects.create_user(
            username=USERNAME, password=PASSWORD)

    def test_redirect_without_login(self):
        # Check that the view redirects to the login screen if the user isn't logged in
        response = self.client.get(reverse("stockapp:balance"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, f"{reverse('login')}?next={reverse('stockapp:balance')}")

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
        self.assertRedirects(
            response, f"{reverse('login')}?next={reverse('stockapp:prices')}")

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
        old_stock1 = Stock.objects.create(ticker="FB", name="Facebook Inc",
                                          price=300.00, change=-3.43)
        portfolio1 = Portfolio.objects.create(
            user=self.user, stock=old_stock1, shares=5)
        old_stock2 = Stock.objects.create(ticker="AMZN", name="Amazon.com Inc",
                                          price=3000.00, change=-35.91)
        portfolio2 = Portfolio.objects.create(
            user=self.user, stock=old_stock2, shares=1)
        old_stock3 = Stock.objects.create(ticker="GOOGL", name="Alphabet Inc",
                                          price=2000.00, change=-3.73)
        portfolio3 = Portfolio.objects.create(
            user=self.user, stock=old_stock3, shares=2)

        self.client.login(username=USERNAME, password=PASSWORD)
        response = self.client.get(reverse("stockapp:prices"))
        new_stock1 = Stock.objects.get(ticker=old_stock1.ticker)
        new_stock2 = Stock.objects.get(ticker=old_stock2.ticker)
        new_stock3 = Stock.objects.get(ticker=old_stock3.ticker)

        self.assertEqual(response.status_code, 200)
        net_worth = (self.user.balance + portfolio1.shares * new_stock1.price
                     + portfolio2.shares * new_stock2.price + portfolio3.shares * new_stock3.price)
        # Convert the Decimals to floats
        prices = [
            {"price": float(new_stock1.price), "change": new_stock1.change},
            {"price": float(new_stock2.price), "change": new_stock2.change},
            {"price": float(new_stock3.price), "change": new_stock3.change}
        ]

        resp = json.loads(response.content)
        # Account for floating point errors by 7 decimal places
        self.assertAlmostEqual(float(resp["netWorth"]), float(net_worth))
        self.assertEqual(resp["prices"], prices)


class CreateAccountView(TestCase):
    # Load all the card data (to successfully redirect to the home page)
    fixtures = ["cards.json"]

    def test_view_renders(self):
        # Check that the view renders properly
        response = self.client.get(reverse("create"))
        self.assertEqual(response.status_code, 200)
        # Check that the title is correct
        self.assertContains(
            response, "<title>Create Account | How to Stock</title>")
        self.assertContains(response, "Login")
        # Check that the relevant content on the create account page is present
        self.assertContains(response, "Username")
        self.assertContains(response, "150 characters or fewer")
        self.assertContains(response, "Password")
        self.assertContains(response, "at least 8 characters")
        self.assertContains(response, "Confirm Password")
        self.assertContains(response, "for verification")
        self.assertContains(response, "Sign Up")
        # Check that the correct context data is passed
        self.assertIsInstance(response.context["form"], CustomUserCreationForm)

    def test_post_form(self):
        # Check that submitting the form redirects the user to the home page
        form_data = {
            "username": USERNAME,
            "password1": PASSWORD,
            "password2": PASSWORD
        }
        form = CustomUserCreationForm(form_data)
        self.assertTrue(form.is_valid())

        response = self.client.post(reverse("create"), form_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("stockapp:index"))
        # Check that the new user is created
        self.assertTrue(User.objects.get(username=USERNAME).is_authenticated)


class DeleteAccountView(TestCase):
    def setUp(self):
        # Create a user that can login to the view
        self.user = get_user_model().objects.create_user(
            username=USERNAME, password=PASSWORD)

    def test_redirect_without_login(self):
        # Check that the view redirects to the login screen if the user isn't logged in
        response = self.client.get(reverse("delete"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, f"{reverse('login')}?next={reverse('delete')}")

    def test_view_renders(self):
        # Check that the view renders properly
        self.client.login(username=USERNAME, password=PASSWORD)
        response = self.client.get(reverse("delete"))
        self.assertEqual(response.status_code, 200)
        # Check that the title is correct
        self.assertContains(
            response, "<title>Delete Account | How to Stock</title>")
        self.assertContains(response, USERNAME)
        # Check that the relevant content on the delete account page is present
        self.assertContains(
            response, "Are you sure you want to delete your account?")
        self.assertContains(response, "You'll lose your portfolio as well.")
        self.assertContains(response, "Yes I'm Sure")
        # Check that the correct context data is passed
        self.assertNotIn("error", response.context)

    def test_post_form(self):
        # Check that submitting the form redirects the user to the login page
        self.client.login(username=USERNAME, password=PASSWORD)
        response = self.client.post(reverse("delete"))
        # Check that the POST request redirects to a successful GET request
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("login"))
        # Check that the user no longer exists
        self.assertQuerysetEqual(User.objects.all(), [])

    def test_delete_superuser(self):
        # Check that deleting a superuser results in an error
        superuser = get_user_model().objects.create_superuser(
            username="superuser", password="superman64")
        self.client.login(username=superuser.username,
                          password="superman64")  # Django doesn't store the raw password
        self.assertTrue(superuser.is_superuser)
        response = self.client.post(reverse("delete"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["error"], f"Delete failed, {superuser} is a superuser")
