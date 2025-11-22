from django.shortcuts import render
from core.models import Team, Player, Report  # Import Team, Player, and Report models


def home_view(request):
    """
    Renders the homepage of the application, displaying top teams, players, and recent public reports.
    """
    # Fetch top 5 teams by position
    teams = Team.objects.filter(position__isnull=False).order_by("position")[:5]  # Get top 5 teams by position
    # Fetch top 5 players by goals
    players = Player.objects.filter(goals__gt=0).order_by("-goals")[:5]  # Get top 5 players by goals

    # Fetch recent public reports
    public_reports = Report.objects.filter(is_public=True).order_by('-created_at') # Get all public reports

    # Create context dictionary
    context = {
        "teams": teams,  # Add teams to context
        "players": players,  # Add players to context
        "public_reports": public_reports, # Add public reports to context
    }
    return render(request, "web/home.html", context)  # Pass context to template
