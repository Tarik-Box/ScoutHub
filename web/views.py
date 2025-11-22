from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail # New import for sending emails
from django.conf import settings # New import for accessing settings
from core.models import Team, Player, Report
from .forms import ContactForm


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


def contact_view(request):
    """
    this view for the contact page. user can send message to admin for any question.
    if user submit the form, we validate it. if its good, show success message then redirect.
    if user just load the page, show the empty form to them.
    """
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']

            # Construct email subject and body
            full_subject = f"ScoutHub Contact Form: {subject} from {name}"
            full_message = f"From: {name} <{email}>\n\n{message}"

            # Get admin email from settings
            admin_email = [admin[1] for admin in settings.ADMINS]

            try:
                send_mail(
                    full_subject,
                    full_message,
                    settings.DEFAULT_FROM_EMAIL,  # From email
                    admin_email,  # To email(s)
                    fail_silently=False,
                )
                messages.success(request, 'Your message has been sent successfully!')
                return redirect('contact')
            except Exception as e:
                messages.error(request, f'There was an error sending your message. Please try again later. Error: {e}')
                # Log the error for debugging
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error sending contact email: {e}", exc_info=True)
                
    else:
        initial_data = {}
        if request.user.is_authenticated:
            initial_data = {
                'name': request.user.username, # Assuming username for name
                'email': request.user.email,
            }
        form = ContactForm(initial=initial_data)
    return render(request, 'web/contact.html', {'form': form})

