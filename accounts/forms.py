from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Profile # Import the Profile model


class CustomUserCreationForm(UserCreationForm):
    """Custom form for user registration, extending Django's UserCreationForm."""

    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + (
            "email",
        )  # Add email to registration form


class ProfileForm(forms.ModelForm):
    """
    Form for users to edit their profile details.
    Allows updates to their bio, profile picture, and scouting preferences.
    """
    class Meta:
        model = Profile
        fields = [
            'bio',
            'profile_picture',
            'preferred_position',
            'idol_player',
            'favorite_talent',
            'best_coach',
            'favorite_club',
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }


from django.contrib.auth.models import User

class UserUpdateForm(forms.ModelForm):
    """
    Form for users to update their core account information.
    Specifically allows changing username and email.
    """
    email = forms.EmailField() # Ensure email field is properly handled

    class Meta:
        model = User
        fields = ['username', 'email']
