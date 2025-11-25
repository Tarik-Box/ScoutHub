"""Forms for creating and updating scouting reports."""
from django import forms
from core.models import Report, Team, Player


class ReportForm(forms.ModelForm):
    """Form for creating and updating scouting reports."""

    # Use ModelChoiceField for single selection dropdown
    team = forms.ModelChoiceField(
        queryset=Team.objects.all(),
        required=False,
        label="Team",
        empty_label="--- Select a Team ---",  # Adds a placeholder
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    # Player dropdown will be populated by JavaScript
    player = forms.ModelChoiceField(
        queryset=Player.objects.none(),  # Initially empty
        required=False,
        label="Player",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    def __init__(self, *args, **kwargs):
        """Initialize the ReportForm."""
        super().__init__(*args, **kwargs)

        # If an instance is provided (i.e., we are editing an existing report)
        if self.instance and self.instance.pk:
            # Set initial value for team (assuming only one team for simplicity as per current form design)
            initial_team = self.instance.teams.first()
            if initial_team:
                self.fields["team"].initial = initial_team
                # Dynamically set the queryset for the player field based on the initial team
                self.fields["player"].queryset = Player.objects.filter(
                    team=initial_team
                )

            # Set initial value for player (assuming only one player for simplicity)
            initial_player = self.instance.players.first()
            if initial_player:
                self.fields["player"].initial = initial_player

    class Meta:
        """Metaclass for the ReportForm."""

        model = Report
        # 'teams' and 'players' are the model's M2M fields, but we use singular
        # 'team' and 'player' in the form for the dynamic dropdowns.
        # The view will handle saving the data to the correct M2M fields.
        fields = ["title", "content", "is_public"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "content": forms.Textarea(attrs={"class": "form-control", "rows": 10}),
            "is_public": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
        labels = {
            "is_public": "Make this report public?",
        }
