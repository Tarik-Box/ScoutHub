"""Views for handling user accounts, authentication, and profiles."""
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from .forms import CustomUserCreationForm, ProfileForm, UserUpdateForm


def register(request):
    """Handles new user registration."""
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
    form_class = CustomLoginForm  # Use our custom login form
    redirect_authenticated_user = (
        True  # Redirects authenticated users away from this view
    )

    def get_success_url(self):
        """Return the URL to redirect to after successful login."""
        return reverse_lazy("home")

    def form_invalid(self, form):
        """
        Renders the invalid login form and adds an error message to the context.
        """
        if self.extra_context is None:
            self.extra_context = {}
        self.extra_context["login_error"] = (
            "Please enter a correct username and password. Note that both fields may be case-sensitive."
        )
        return super().form_invalid(form)


@login_required
def profile_view(request):
    """
    Handles displaying and updating a user's profile.

    On GET, it shows the current user's profile data in editable forms.
    On POST, it processes updates to both the User and Profile models.
    """
    if request.method == "POST":
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileForm(
            request.POST, request.FILES, instance=request.user.profile
        )

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Your profile was successfully updated!")
            return redirect("accounts:profile")
        else:
            messages.error(request, "Please correct the error below.")
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)

    context = {"user_form": user_form, "profile_form": profile_form}
    return render(request, "accounts/profile.html", context)