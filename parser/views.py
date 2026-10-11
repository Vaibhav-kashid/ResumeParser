from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ResumeUploadForm
from .models import Candidate, UploadedResume
from .services.resume_service import process_resume


@login_required
def upload_resume(request):
    if request.method == "POST":
        form = ResumeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            resume = form.save(commit=False)
            resume.user = request.user
            resume.original_filename = request.FILES["file"].name
            resume.save()
            try:
                process_resume(resume)
                messages.success(request, "Resume parsed successfully.")
                return redirect("candidate_profile", pk=resume.candidate.pk)
            except Exception as exc:
                messages.error(request, f"Could not parse this resume: {exc}")
                return redirect("upload_resume")
    else:
        form = ResumeUploadForm()
    return render(request, "parser/upload.html", {"form": form})


@login_required
def candidate_profile(request, pk):
    candidate = get_object_or_404(Candidate, pk=pk, user=request.user)
    return render(request, "parser/profile.html", {"candidate": candidate})


@login_required
def candidate_profile_edit(request, pk):
    candidate = get_object_or_404(Candidate, pk=pk, user=request.user)
    if request.method == "POST":
        candidate.name = request.POST.get("name", candidate.name)
        candidate.email = request.POST.get("email", candidate.email)
        candidate.phone = request.POST.get("phone", candidate.phone)
        candidate.address = request.POST.get("address", candidate.address)
        candidate.summary = request.POST.get("summary", candidate.summary)
        candidate.save()
        messages.success(request, "Profile updated.")
        return redirect("candidate_profile", pk=candidate.pk)
    return render(request, "parser/profile_edit.html", {"candidate": candidate})
