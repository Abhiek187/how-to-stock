from django.test import TestCase
from django.urls import reverse

from stockapp.models import Card


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
