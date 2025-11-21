from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.views import LoginView  # NEW IMPORT
from .forms import CustomUserCreationForm
from django.urls import reverse_lazy  # NEW IMPORT


def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log the user in immediately after registration
            return redirect("home")  # Redirect to homepage or dashboard
    else:
        form = CustomUserCreationForm()
    return render(request, "accounts/register.html", {"form": form})


class CustomLoginView(LoginView):
    """Custom view for user login, extending Django's built-in LoginView."""

    template_name = "accounts/login.html"
    fields = "__all__"
    redirect_authenticated_user = (
        True  # Redirects authenticated users away from this view
    )

    def get_success_url(self):
        return reverse_lazy("home")  # Redirect to 'home' on successful login
