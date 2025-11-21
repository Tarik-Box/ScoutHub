from django.urls import path
from . import views

app_name = "reports"

urlpatterns = [
    path("create/", views.create_report, name="create_report"),
    path("<int:report_id>/", views.report_detail, name="report_detail"),
    path("<int:report_id>/edit/", views.edit_report, name="edit_report"),
]
