from django.test import TestCase
from django.urls import reverse

from .forms import ScreenerForm
from .models import Card, Stock

# Create tests for each view
class HomeViewTests(TestCase):
    # All test functions must start with test*
    def test_view_renders(self):
        # Check that the view renders properly
        response = self.client.get(reverse("stockapp:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Welcome!")
        self.assertQuerysetEqual(response.context["dummy_list"], [])


class ScreenerViewTests(TestCase):
    def test_view_renders(self):
        # Check that the view renders properly
        response = self.client.get(reverse("stockapp:screener"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "</form>")
        self.assertEqual(response.context["results"], None)


class DetailViewTests(TestCase):
    def test_view_renders(self):
        # Check that the view renders properly
        response = self.client.get(reverse("stockapp:detail", args=("PRU",)))
        session = self.client.session
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "predict")
        self.assertEqual(response.context["balance"], session["balance"])


class FlashcardsViewTests(TestCase):
    def test_view_renders(self):
        # Check that the view renders properly
        response = self.client.get(reverse("stockapp:flashcards"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "card")
        self.assertQuerysetEqual(response.context["cards"], [])


class PortfolioViewTests(TestCase):
    def test_view_renders(self):
        # Check that the view renders properly
        response = self.client.get(reverse("stockapp:portfolio"))
        session = self.client.session
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Balance")
        self.assertContains(response, "Net Worth")
        self.assertEqual(response.context["balance"], session["balance"])
        self.assertGreaterEqual(response.context["net_worth"], response.context["balance"])


class BalanceViewTests(TestCase):
    def test_view_renders(self):
        # Check that the view renders properly
        response = self.client.get(reverse("stockapp:balance"))
        session = self.client.session
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, session.get("balance", 10000))
