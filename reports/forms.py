from django import forms
from core.models import Report, Team, Player

class ReportForm(forms.ModelForm):
    teams = forms.ModelMultipleChoiceField(
        queryset=Team.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    players = forms.ModelMultipleChoiceField(
        queryset=Player.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Report
        fields = ['title', 'content', 'teams', 'players', 'is_public']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 10}),
        }
        labels = {
            'is_public': 'Make this report public?',
        }
