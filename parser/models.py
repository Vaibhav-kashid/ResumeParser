from django.conf import settings
from django.db import models


class UploadedResume(models.Model):
    """Raw uploaded resume file, tied to the user who uploaded it."""

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("parsed", "Parsed"),
        ("failed", "Failed"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="resumes")
    file = models.FileField(upload_to="resumes/%Y/%m/")
    original_filename = models.CharField(max_length=255)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    parsed_at = models.DateTimeField(null=True, blank=True)
    raw_text = models.TextField(blank=True)
    error_message = models.CharField(max_length=500, blank=True)

    def __str__(self):
        return f"{self.original_filename} ({self.status})"


class Candidate(models.Model):
    """Structured profile extracted from a parsed resume."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="candidates")
    resume = models.OneToOneField(UploadedResume, on_delete=models.CASCADE, related_name="candidate")
    name = models.CharField(max_length=150, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    address = models.CharField(max_length=255, blank=True)
    linkedin_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    summary = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name or f"Candidate #{self.pk}"


class Education(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name="education")
    institution = models.CharField(max_length=255, blank=True)
    degree = models.CharField(max_length=255, blank=True)
    year = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.degree} - {self.institution}"


class Experience(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name="experience")
    company = models.CharField(max_length=255, blank=True)
    role = models.CharField(max_length=255, blank=True)
    duration = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.role} at {self.company}"


class Skill(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name="skills")
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Certification(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name="certifications")
    name = models.CharField(max_length=255)
    issuer = models.CharField(max_length=255, blank=True)
    year = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.name
