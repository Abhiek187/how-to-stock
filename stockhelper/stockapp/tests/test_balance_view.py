from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .utils import USERNAME, PASSWORD


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
