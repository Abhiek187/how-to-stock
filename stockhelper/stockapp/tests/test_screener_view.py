from django.test import TestCase
from django.urls import reverse

from stockapp.forms import ScreenerForm


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
