from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from core.models import Report


@login_required
def dashboard(request):
    # Fetch reports created by the currently logged-in user, order by most recent
    user_reports = Report.objects.filter(user=request.user).order_by("-created_at")

    context = {"reports": user_reports}
    return render(request, "dashboard/dashboard.html", context)
