from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from core.models import Report
from django.core.paginator import Paginator


@login_required
def dashboard(request):
    # Fetch reports created by the currently logged-in user, order by most recent
    report_list = Report.objects.filter(user=request.user).order_by("-created_at")
    
    # Set up pagination
    paginator = Paginator(report_list, 5)  # Show 5 reports per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {"page_obj": page_obj}
    return render(request, "dashboard/dashboard.html", context)
