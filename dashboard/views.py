import csv

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render

from parser.models import Candidate


@login_required
def dashboard_home(request):
    candidates = Candidate.objects.filter(user=request.user).prefetch_related("skills", "education", "experience")

    query = request.GET.get("q", "").strip()
    skill_filter = request.GET.get("skill", "").strip()

    if query:
        candidates = candidates.filter(
            Q(name__icontains=query) | Q(email__icontains=query) | Q(phone__icontains=query)
        )
    if skill_filter:
        candidates = candidates.filter(skills__name__icontains=skill_filter).distinct()

    context = {
        "candidates": candidates,
        "query": query,
        "skill_filter": skill_filter,
        "total_count": Candidate.objects.filter(user=request.user).count(),
    }
    return render(request, "dashboard/home.html", context)


@login_required
def export_csv(request):
    candidates = Candidate.objects.filter(user=request.user).prefetch_related("skills")

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="candidates.csv"'

    writer = csv.writer(response)
    writer.writerow(["Name", "Email", "Phone", "Skills", "Uploaded At"])
    for c in candidates:
        skills = ", ".join(s.name for s in c.skills.all())
        writer.writerow([c.name, c.email, c.phone, skills, c.created_at])
    return response
