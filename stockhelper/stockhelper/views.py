from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse

from .forms import CustomUserCreationForm, DeleteUserForm


# Create Account view
def create_account(request):
    status = 200

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
            return redirect(reverse("stockapp:index"))
        else:
            status = 400
    else:
        form = CustomUserCreationForm()

    return render(request, "registration/create.html", {"form": form}, status=status)


# Delete Account view
@login_required
def delete_account(request):
    if request.method == "POST":
        form = DeleteUserForm(request.POST)

        if form.is_valid():
            # Check if the username field is correct
            username = form.cleaned_data.get("username")

            if username != request.user.username:
                return render(request, "registration/delete.html", {
                    "error": f"Incorrect username: {username}"
                }, status=400)
            # Safeguard to avoid losing access to the admin page
            elif request.user.is_superuser:
                return render(request, "registration/delete.html", {
                    "error": f"Delete failed, {request.user} is a superuser"
                }, status=400)
            else:
                # Delete the user object and redirect to the login page
                request.user.delete()
                return redirect(reverse("login"))

    return render(request, "registration/delete.html")
