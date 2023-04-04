from django import forms
from django.contrib.auth.forms import BaseUserCreationForm

from stockapp.models import User


class CustomUserCreationForm(BaseUserCreationForm):
    # Required to create a new custom user
    class Meta(BaseUserCreationForm.Meta):
        model = User
        fields = BaseUserCreationForm.Meta.fields


class DeleteUserForm(forms.Form):
    # Usernames are 150 characters or less
    username = forms.CharField(max_length=150)
