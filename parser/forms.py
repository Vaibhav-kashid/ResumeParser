from django import forms
from django.conf import settings

from .models import UploadedResume

ALLOWED_EXTENSIONS = [".pdf", ".docx"]


class ResumeUploadForm(forms.ModelForm):
    class Meta:
        model = UploadedResume
        fields = ["file"]
        widgets = {
            "file": forms.ClearableFileInput(attrs={"class": "form-control", "accept": ".pdf,.docx"}),
        }

    def clean_file(self):
        file = self.cleaned_data["file"]
        name = file.name.lower()
        if not any(name.endswith(ext) for ext in ALLOWED_EXTENSIONS):
            raise forms.ValidationError("Only PDF and DOCX files are supported.")
        max_size = getattr(settings, "MAX_RESUME_UPLOAD_SIZE_MB", 5) * 1024 * 1024
        if file.size > max_size:
            raise forms.ValidationError(f"File too large. Max size is {settings.MAX_RESUME_UPLOAD_SIZE_MB} MB.")
        return file
