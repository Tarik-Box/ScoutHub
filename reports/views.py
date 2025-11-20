from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ReportForm

@login_required
def create_report(request):
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.user = request.user
            report.save()
            form.save_m2m()  # Needed for ManyToMany fields
            return redirect('home')
    else:
        form = ReportForm()
    return render(request, 'reports/create_report.html', {'form': form})

