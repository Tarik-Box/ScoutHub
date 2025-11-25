"""URL patterns for the accounts app."""
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views  # Django's built-in logout
from django.urls import reverse_lazy  # LogoutView next_page

app_name = "accounts"  # Namespace for this app's URLs

urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.CustomLoginView.as_view(), name="login"),
    path(
        "logout/",
        auth_views.LogoutView.as_view(next_page=reverse_lazy("home")),
        name="logout",
    ),
    path("profile/", views.profile_view, name="profile"),
]
