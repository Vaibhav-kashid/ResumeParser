from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard_home, name="dashboard"),
    path("export/csv/", views.export_csv, name="export_csv"),
]
