from django.shortcuts import render
from core.models import Team, Player # Import Team and Player models

def home_view(request):
    """
    Renders the homepage of the application, displaying top teams and players.
    """
    # Fetch a few teams and players from the database
    # For now, just getting all, later we can implement 'top 5' logic
    teams = Team.objects.all()[:5]  # Get top 5 teams
    players = Player.objects.all()[:5] # Get top 5 players

    context = { # Create context dictionary
        'teams': teams, # Add teams to context
        'players': players, # Add players to context
    }
    return render(request, 'web/home.html', context) # Pass context to template
