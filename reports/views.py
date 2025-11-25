"""Views for handling scouting reports."""

from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from weasyprint import HTML as WeasyPrint
from .forms import ReportForm
from core.models import Player, Report
import json


@login_required
def toggle_report_visibility(request, report_id):
    """
    Toggles the 'is_public' status of a report.

    Only accessible via POST request by the report owner.
    """
    report = get_object_or_404(Report, pk=report_id)

    if report.user != request.user:
        raise Http404(
            "You do not have permission to change the visibility of this report."
        )

    if request.method == "POST":
        report.is_public = not report.is_public
        report.save()
        messages.success(
            request,
            f"Report visibility changed to {'Public' if report.is_public else 'Private'}.",
        )

    return redirect("reports:report_detail", report_id=report.id)


@login_required
def report_detail(request, report_id):
    """Display details of a scouting report."""
    report = get_object_or_404(Report, pk=report_id)

    if report.user != request.user and not report.is_public:
        raise Http404("You do not have permission to view this report.")

    context = {"report": report}
    return render(request, "reports/report_detail.html", context)


@login_required
def export_report_pdf(request, report_id):
    """Export a scouting report as a PDF file."""
    report = get_object_or_404(Report, pk=report_id)

    if report.user != request.user:
        raise Http404("You do not have permission to download this report.")

    html_string = render_to_string(
        "reports/report_pdf_template.html", {"report": report, "request": request}
    )

    try:
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = (
            f'attachment; filename="scouting_report_{report.id}.pdf"'
        )

        pdf = WeasyPrint(
            string=html_string, base_url=request.build_absolute_uri("/")
        ).write_pdf()
        response.write(pdf)

        return response
    except Exception as e:
        messages.error(request, f"Could not generate the PDF file. Error: {e}")
        import logging

        logger = logging.getLogger(__name__)
        logger.error(f"Error generating PDF for report {report.id}: {e}", exc_info=True)
        return redirect("reports:report_detail", report_id=report.id)


@login_required
def edit_report(request, report_id):
    """Handle editing an existing scouting report."""
    report = get_object_or_404(Report, pk=report_id)

    if report.user != request.user:
        raise Http404("You do not have permission to edit this report.")

    if request.method == "POST":
        form = ReportForm(request.POST, instance=report)

        team_id = request.POST.get("team")
        if team_id:
            form.fields["player"].queryset = Player.objects.filter(team_id=team_id)

        if form.is_valid():
            edited_report = form.save(commit=False)
            edited_report.user = request.user
            edited_report.save()

            team = form.cleaned_data.get("team")
            player = form.cleaned_data.get("player")

            edited_report.teams.set([team] if team else [])
            edited_report.players.set([player] if player else [])

            messages.success(request, "Report updated successfully!")
            return redirect("reports:report_detail", report_id=report.id)
    else:
        form = ReportForm(instance=report)

        if report.teams.first():
            initial_team_id = report.teams.first().id
            form.fields["player"].queryset = Player.objects.filter(
                team_id=initial_team_id
            )

    players_in_db = Player.objects.select_related("team").all()
    players_data = {}
    for player_obj in players_in_db:
        if player_obj.team.id not in players_data:
            players_data[player_obj.team.id] = []
        players_data[player_obj.team.id].append(
            {"id": player_obj.id, "name": player_obj.name}
        )

    context = {
        "form": form,
        "report": report,
        "players_data_json": json.dumps(players_data),
    }
    return render(request, "reports/create_report.html", context)


@login_required
def delete_report(request, report_id):
    """Handle deletion of a scouting report."""
    report = get_object_or_404(Report, pk=report_id)

    if report.user != request.user:
        raise Http404("You do not have permission to delete this report.")

    if request.method == "POST":
        report.delete()
        messages.success(request, "Report deleted successfully!")
        return redirect("dashboard:user_dashboard")

    messages.error(request, "Invalid request for report deletion.")
    return redirect("dashboard:user_dashboard")


@login_required
def create_report(request):
    """Handle creation of a new scouting report."""
    if request.method == "POST":
        form = ReportForm(request.POST)

        team_id = request.POST.get("team")
        if team_id:
            form.fields["player"].queryset = Player.objects.filter(team_id=team_id)

        if form.is_valid():
            report = form.save(commit=False)
            report.user = request.user
            report.save()

            team = form.cleaned_data.get("team")
            player = form.cleaned_data.get("player")

            report.teams.set([team] if team else [])
            report.players.set([player] if player else [])

            messages.success(request, "Report created successfully!")
            return redirect("dashboard:user_dashboard")
    else:
        form = ReportForm()

    players = Player.objects.select_related("team").all()
    players_data = {}
    for player_obj in players:
        if player_obj.team.id not in players_data:
            players_data[player_obj.team.id] = []
        players_data[player_obj.team.id].append(
            {"id": player_obj.id, "name": player_obj.name}
        )

    context = {"form": form, "players_data_json": json.dumps(players_data)}
    return render(request, "reports/create_report.html", context)
