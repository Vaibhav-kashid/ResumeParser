from django.urls import path

from . import views

urlpatterns = [
    path("upload/", views.upload_resume, name="upload_resume"),
    path("candidate/<int:pk>/", views.candidate_profile, name="candidate_profile"),
    path("candidate/<int:pk>/edit/", views.candidate_profile_edit, name="candidate_profile_edit"),
]
