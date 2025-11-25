"""Custom forms for the accounts app."""

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Profile  # Import the Profile model


class CustomLoginForm(AuthenticationForm):
    """
    Custom login form to apply Bootstrap's 'form-control' class.

    This is for consistent styling of the input fields.
    """

    def __init__(self, *args, **kwargs):
        """Initialize the form and add 'form-control' class to all fields."""
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({"class": "form-control"})


class CustomUserCreationForm(UserCreationForm):
    """Custom form for user registration, extending Django's UserCreationForm."""

    def __init__(self, *args, **kwargs):
        """Initialize the form and add 'form-control' class to all fields."""
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({"class": "form-control"})

    class Meta(UserCreationForm.Meta):
        """Metaclass to add the email field to the registration form."""

        fields = UserCreationForm.Meta.fields + (
            "email",
        )  # Add email to registration form


class ProfileForm(forms.ModelForm):
    """
    Form for users to edit their profile details.

    Allows updates to their bio, profile picture, and scouting preferences.
    """

    def __init__(self, *args, **kwargs):
        """Initialize the form and apply Bootstrap classes."""
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name == "profile_picture":  # Special handling for FileInput
                field.widget.attrs.update({"class": "form-control-file"})
            else:
                field.widget.attrs.update({"class": "form-control"})

    class Meta:
        """Metaclass for ProfileForm."""

        model = Profile
        fields = [
            "bio",
            "profile_picture",
            "preferred_position",
            "idol_player",
            "favorite_talent",
            "best_coach",
            "favorite_club",
        ]
        widgets = {
            "bio": forms.Textarea(
                attrs={"rows": 4, "class": "form-control"}
            ),  # Ensure form-control on bio as well
        }


class UserUpdateForm(forms.ModelForm):
    """
    Form for users to update their core account information.

    Specifically allows changing username and email.
    """

    email = forms.EmailField()  # Ensure email field is properly handled

    def __init__(self, *args, **kwargs):
        """Initialize the form and add 'form-control' class to all fields."""
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({"class": "form-control"})

    class Meta:
        """Metaclass for UserUpdateForm."""

        model = User
        fields = ["username", "email"]
