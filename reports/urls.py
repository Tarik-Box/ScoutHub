"""URL patterns for the reports app."""

from django.urls import path
from . import views

app_name = "reports"

urlpatterns = [
    path("create/", views.create_report, name="create_report"),
    path("<int:report_id>/", views.report_detail, name="report_detail"),
    path("<int:report_id>/edit/", views.edit_report, name="edit_report"),
    path(
        "<int:report_id>/toggle_visibility/",
        views.toggle_report_visibility,
        name="toggle_report_visibility",
    ),
    path("<int:report_id>/delete/", views.delete_report, name="delete_report"),
    path("<int:report_id>/pdf/", views.export_report_pdf, name="export_report_pdf"),
]
