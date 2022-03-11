from django.test import TestCase
from django.urls import reverse


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
