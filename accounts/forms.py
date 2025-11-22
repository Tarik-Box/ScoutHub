from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm


class CustomUserCreationForm(UserCreationForm):
    """Custom form for user registration, extending Django's UserCreationForm."""

    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + (
            "email",
        )  # Add email to registration form

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name != 'password2': # password2 is a confirm password field
                field.widget.attrs.update({'class': 'input', 'placeholder': field.label})
            else:
                field.widget.attrs.update({'class': 'input', 'placeholder': 'Confirm Password'})


class CustomAuthenticationForm(AuthenticationForm):
    """
    This here custom form for the log-in page. user can log in with this.
    we just want to add some nice classes for styling, ya know.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'input', 'placeholder': field.label})
