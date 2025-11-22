from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponse # MODIFIED: Added HttpResponse
from django.contrib import messages  # NEW IMPORT
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string # NEW IMPORT
from weasyprint import HTML as WeasyPrint # NEW IMPORT
from .forms import ReportForm
from core.models import Team, Player, Report
import json


@login_required
def toggle_report_visibility(request, report_id):
    """
    Toggles the 'is_public' status of a report.
    Only accessible via POST request by the report owner.
    """
    report = get_object_or_404(Report, pk=report_id)

    # Access control: Only the owner can toggle visibility
    if report.user != request.user:
        raise Http404("You do not have permission to change the visibility of this report.")

    if request.method == "POST":
        report.is_public = not report.is_public
        report.save()
        messages.success(
            request, f"Report visibility changed to {'Public' if report.is_public else 'Private'}."
        )
    
    return redirect("reports:report_detail", report_id=report.id)


@login_required
def report_detail(request, report_id):
    """
    Displays the details of a specific scouting report.
    """
    report = get_object_or_404(Report, pk=report_id)

    # Ensure that the logged-in user is the author of the report, or if the report is public
    if report.user != request.user and not report.is_public:
        raise Http404("You do not have permission to view this report.")

    context = {
        "report": report
    }
    return render(request, "reports/report_detail.html", context)


@login_required
def export_report_pdf(request, report_id):
    """
    this view for exportin' a scouting report as a PDF file, you know, for shar'n.
    it takes the report data, puts it in a nice HTML template, then turns it into PDF.
    only report owners can download their stuff, for security reasons, obv.
    """
    report = get_object_or_404(Report, pk=report_id)

    # Access control: Only the owner can download the report
    if report.user != request.user:
        raise Http404("You do not have permission to download this report.")

    # Render HTML content with report data
    html_string = render_to_string('reports/report_pdf_template.html', {'report': report, 'request': request})

    # Generate PDF using WeasyPrint
    try:
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="scouting_report_{report.id}.pdf"'
        
        # WeasyPrint expects bytes, so encode the HTML string
        pdf = WeasyPrint(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf()
        response.write(pdf)
        
        return response
    except Exception as e:
        messages.error(request, f"Whoops! Couldn't make the PDF file. Error: {e}")
        # Log this error for later investigation.
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error generating PDF for report {report.id}: {e}", exc_info=True)
        return redirect('reports:report_detail', report_id=report.id) # Redirect back to report detail page with an error


@login_required
def edit_report(request, report_id):
    """
    Handles editing an existing scouting report.

    On GET, displays a form pre-filled with the report's data.
    On POST, validates submitted data and updates the report.
    """
    report = get_object_or_404(Report, pk=report_id)

    # Access control: Only the owner can edit the report
    if report.user != request.user:
        raise Http404("You do not have permission to edit this report.")

    if request.method == "POST":
        form = ReportForm(request.POST, instance=report)

        # Dynamically update the queryset for the 'player' field before validation.
        team_id = request.POST.get("team")
        if team_id:
            form.fields["player"].queryset = Player.objects.filter(team_id=team_id)
        # If no team_id is provided, the queryset will remain Player.objects.none()
        # which means validation for player will always fail unless player is not required.

        if form.is_valid():
            # Save the main report fields
            edited_report = form.save(commit=False)
            edited_report.user = request.user  # Ensure user remains the original author
            edited_report.save()

            # Handle ManyToMany fields for team and player
            team = form.cleaned_data.get("team")
            player = form.cleaned_data.get("player")

            # Update the M2M relations. If empty, clear them.
            edited_report.teams.set([team] if team else [])
            edited_report.players.set([player] if player else [])

            messages.success(request, "Report updated successfully!")  # NEW
            return redirect("reports:report_detail", report_id=report.id)
    else:  # GET request
        # Pre-fill the form with existing report data
        form = ReportForm(instance=report)

        # For GET request, if a team is already selected in the instance,
        # update the player queryset for the initial display.
        if report.teams.first():
            initial_team_id = report.teams.first().id
            form.fields["player"].queryset = Player.objects.filter(
                team_id=initial_team_id
            )

    # Prepare data for the dependent dropdowns for the template
    # This is similar to create_report to ensure JS has data on both GET/POST
    players_in_db = Player.objects.select_related("team").all()
    print("DEBUG (edit_report): Number of players in queryset:", players_in_db.count()) # NEW DEBUG PRINT
    players_data = {}
    for player_obj in players_in_db:
        if player_obj.team.id not in players_data:
            players_data[player_obj.team.id] = []
        players_data[player_obj.team.id].append(
            {"id": player_obj.id, "name": player_obj.name}
        ) # MISSING LINE ADDED
    print("DEBUG (edit_report): players_data before json.dumps:", players_data) # NEW DEBUG PRINT

    context = {
        "form": form,
        "report": report,  # Pass the report object for dynamic title and other context
        "players_data_json": json.dumps(players_data),
    }
    return render(request, "reports/create_report.html", context)


@login_required
def delete_report(request, report_id):
    """
    Handles the deletion of a scouting report.
    Only allows deletion by the report owner via a POST request.
    """
    report = get_object_or_404(Report, pk=report_id)

    # Access control: Only the owner can delete the report
    if report.user != request.user:
        raise Http404("You do not have permission to delete this report.")

    if request.method == "POST":
        report.delete()
        messages.success(request, "Report deleted successfully!")
        return redirect("dashboard:user_dashboard")
    
    # If it's a GET request to the delete URL, perhaps render a confirmation page
    # For now, we'll just redirect to the dashboard if not a POST.
    # In a real application, you might want a confirmation modal/page.
    messages.error(request, "Invalid request for report deletion.")
    return redirect("dashboard:user_dashboard")


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

            # Add a success message for report creation
            messages.success(request, "Report created successfully!")
            return redirect("dashboard:user_dashboard")
    else: # GET request
        form = ReportForm()

    # Prepare data for the dependent dropdowns
    players = Player.objects.select_related("team").all()
    print("DEBUG (create_report): Number of players in queryset:", players.count()) # NEW DEBUG PRINT
    players_data = {}
    for player_obj in players:
        if player_obj.team.id not in players_data:
            players_data[player_obj.team.id] = []
        players_data[player_obj.team.id].append({"id": player_obj.id, "name": player_obj.name})
    print("DEBUG (create_report): players_data before json.dumps:", players_data) # NEW DEBUG PRINT

    context = {"form": form, "players_data_json": json.dumps(players_data)}
    return render(request, "reports/create_report.html", context)
