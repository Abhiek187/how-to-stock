from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from stockapp.models import User
from stockhelper.forms import DeleteUserForm
from utils_test import USERNAME, PASSWORD


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
        self.assertContains(response, "Please type your username to confirm.")
        self.assertContains(response, "Delete Account")
        # Check that the correct context data is passed
        self.assertNotIn("error", response.context)

    def test_post_form(self):
        # Check that submitting the form redirects the user to the login page
        form_data = {
            "username": USERNAME
        }
        form = DeleteUserForm(form_data)
        self.assertTrue(form.is_valid())

        self.client.login(username=USERNAME, password=PASSWORD)
        response = self.client.post(reverse("delete"), form_data)

        # Check that the POST request redirects to a successful GET request
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("login"))
        # Check that the user no longer exists
        self.assertQuerysetEqual(User.objects.all(), [])
    
    def test_invalid_username(self):
        # Check that entering the wrong username prevents the user from being deleted
        wrong_username = f"{USERNAME}?"
        form_data = {
            "username": wrong_username
        }
        form = DeleteUserForm(form_data)
        self.assertTrue(form.is_valid())

        self.client.login(username=USERNAME, password=PASSWORD)
        response = self.client.post(reverse("delete"), form_data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.context["error"], f"Incorrect username: {wrong_username}")
        # get will raise an exception
        self.assertTrue(User.objects.filter(username=USERNAME).exists())

    def test_delete_superuser(self):
        # Check that deleting a superuser results in an error
        superuser = get_user_model().objects.create_superuser(
            username="superuser", password="superman64")
        form_data = {
            "username": superuser.username
        }
        form = DeleteUserForm(form_data)
        self.assertTrue(form.is_valid())

        self.client.login(username=superuser.username,
                          password="superman64")  # Django doesn't store the raw password
        self.assertTrue(superuser.is_superuser)
        response = self.client.post(reverse("delete"), form_data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.context["error"], f"Delete failed, {superuser} is a superuser")
        self.assertTrue(User.objects.filter(username=USERNAME).exists())
