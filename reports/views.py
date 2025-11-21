from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ReportForm
from core.models import Team, Player
import json


@login_required
def create_report(request):
    if request.method == "POST":
        form = ReportForm(request.POST)
        if form.is_valid():
            # Create the report instance but don't save to DB yet
            report = form.save(commit=False)
            report.user = request.user
            report.save()  # Save the report object to get an ID

            # Now handle the ManyToMany fields from the form
            team = form.cleaned_data.get("team")
            player = form.cleaned_data.get("player")

            # Clear any existing relations and add the new ones
            report.teams.set([team] if team else [])
            report.players.set([player] if player else [])

            return redirect("dashboard:user_dashboard")  # Redirect to dashboard
    else:
        form = ReportForm()

    # Prepare data for the dependent dropdowns
    players = Player.objects.select_related("team").all()
    players_data = {}
    for player in players:
        if player.team.id not in players_data:
            players_data[player.team.id] = []
        players_data[player.team.id].append({"id": player.id, "name": player.name})

    context = {"form": form, "players_data_json": json.dumps(players_data)}
    return render(request, "reports/create_report.html", context)
