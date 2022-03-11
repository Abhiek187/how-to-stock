from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from stockapp.models import User
from .utils import USERNAME, PASSWORD


class DeleteAccountViewTests(TestCase):
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
