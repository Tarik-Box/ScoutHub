from django.shortcuts import render
from core.models import Team, Player  # Import Team and Player models


def home_view(request):
    """
    Renders the homepage of the application, displaying top teams and players.
    """
    # Fetch a few teams and players from the database
    # For now, just getting all, later we can implement 'top 5' logic
    teams = Team.objects.filter(position__isnull=False).order_by("position")[:5]  # Get top 5 teams by position
    players = Player.objects.filter(goals__gt=0).order_by("-goals")[:5]  # Get top 5 players by goals

    # Create context dictionary
    context = {
        "teams": teams,  # Add teams to context
        "players": players,  # Add players to context
    }
    return render(request, "web/home.html", context)  # Pass context to template
