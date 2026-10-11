"""Orchestrates the end-to-end parsing workflow:
extract text -> parse fields -> persist Candidate + related rows.
"""
from django.utils import timezone

from parser.models import Candidate, Certification, Education, Experience, Skill
from parser.services.field_parser import parse_fields
from parser.services.text_extraction import extract_text


def process_resume(uploaded_resume):
    """Given an UploadedResume instance, extract + parse + save a Candidate.

    Returns the created/updated Candidate. Updates uploaded_resume.status
    in place (parsed/failed) so the UI can reflect progress.
    """
    try:
        text = extract_text(uploaded_resume.file.path)
        uploaded_resume.raw_text = text
        fields = parse_fields(text)

        candidate, _ = Candidate.objects.update_or_create(
            resume=uploaded_resume,
            defaults={
                "user": uploaded_resume.user,
                "name": fields["name"],
                "email": fields["email"],
                "phone": fields["phone"],
                "linkedin_url": fields["linkedin_url"],
                "github_url": fields["github_url"],
            },
        )

        # Replace child rows on re-parse to avoid duplicates
        candidate.skills.all().delete()
        candidate.education.all().delete()
        candidate.experience.all().delete()

        Skill.objects.bulk_create([
            Skill(candidate=candidate, name=s) for s in fields["skills"]
        ])
        Education.objects.bulk_create([
            Education(candidate=candidate, institution=e["institution"], degree=e["degree"], year=e["year"])
            for e in fields["education"]
        ])
        Experience.objects.bulk_create([
            Experience(candidate=candidate, company=e["company"], role=e["role"], duration=e["duration"])
            for e in fields["experience"]
        ])

        uploaded_resume.status = "parsed"
        uploaded_resume.parsed_at = timezone.now()
        uploaded_resume.error_message = ""
        uploaded_resume.save()
        return candidate

    except Exception as exc:
        uploaded_resume.status = "failed"
        uploaded_resume.error_message = str(exc)[:500]
        uploaded_resume.save()
        raise
