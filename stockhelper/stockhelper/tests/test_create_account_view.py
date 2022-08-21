from django.test import TestCase
from django.urls import reverse

from stockapp.models import User
from stockhelper.forms import CustomUserCreationForm
from utils_test import USERNAME, PASSWORD


class CreateAccountViewTests(TestCase):
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
    
    def test_invalid_user(self):
        # Check that entering an invalid user doesn't create a new user
        bad_username = "~!@#$%^&*()_+"
        form_data = {
            "username": bad_username,
            "password1": "1234",
            "password2": "1234"
        }
        form = CustomUserCreationForm(form_data)
        self.assertFalse(form.is_valid())

        response = self.client.post(reverse("create"), form_data)
        self.assertEqual(response.status_code, 400)
        self.assertQuerysetEqual(User.objects.all(), [])
