from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render

from .forms import CustomUserCreationForm


# Create Account view
def create_account(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)

        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            # password1 and password2 should match
            password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=password)
            login(request, user)
            # Upon successful creation of the account, redirect the user to the home page
            return redirect("/stockapp")
    else:
        form = CustomUserCreationForm()

    return render(request, "registration/create.html", {"form": form})
