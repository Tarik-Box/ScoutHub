from django.shortcuts import render

def home_view(request):
    """
    Renders the homepage of the application.
    """
    return render(request, 'web/home.html', {})