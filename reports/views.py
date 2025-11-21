from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.contrib.auth.decorators import login_required
from .forms import ReportForm
from core.models import Team, Player, Report
import json


@login_required
def create_report(request):
    """
    Handles the creation of a new scouting report.

    On GET, displays an empty form.
    On POST, validates submitted data, including dynamically populated
    player choices, and saves the new report.
    """
    if request.method == "POST":
        form = ReportForm(request.POST)

        # Dynamically update the queryset for the 'player' field before validation.
        team_id = request.POST.get("team")
        if team_id:
            form.fields["player"].queryset = Player.objects.filter(team_id=team_id)

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


@login_required
def report_detail(request, report_id):
    """
    Displays the details of a specific scouting report.
    """
    report = get_object_or_404(Report, pk=report_id)

    # Ensure that the logged-in user is the author of the report
    if report.user != request.user:
        raise Http404("You do not have permission to view this report.")

    context = {
        'report': report
    }
    return render(request, 'reports/report_detail.html', context)
