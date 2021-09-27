from django.contrib.auth.forms import UserCreationForm

from stockapp.models import User


class CustomUserCreationForm(UserCreationForm):
    # Required to create a new custom user
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields
