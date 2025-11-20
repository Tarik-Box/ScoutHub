from django import forms
from core.models import Report, Team, Player

class ReportForm(forms.ModelForm):
    # Use ModelChoiceField for single selection dropdown
    team = forms.ModelChoiceField(
        queryset=Team.objects.all(),
        required=False,
        label="Team",
        empty_label="--- Select a Team ---", # Adds a placeholder
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    # Player dropdown will be populated by JavaScript
    player = forms.ModelChoiceField(
        queryset=Player.objects.none(), # Initially empty
        required=False,
        label="Player",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Report
        # 'teams' and 'players' are the model's M2M fields, but we use singular
        # 'team' and 'player' in the form for the dynamic dropdowns.
        # The view will handle saving the data to the correct M2M fields.
        fields = ['title', 'content', 'is_public']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'is_public': 'Make this report public?',
        }

