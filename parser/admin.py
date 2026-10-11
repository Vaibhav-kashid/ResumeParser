from django.contrib import admin

from .models import Candidate, Certification, Education, Experience, Skill, UploadedResume


class EducationInline(admin.TabularInline):
    model = Education
    extra = 0


class ExperienceInline(admin.TabularInline):
    model = Experience
    extra = 0


class SkillInline(admin.TabularInline):
    model = Skill
    extra = 0


class CertificationInline(admin.TabularInline):
    model = Certification
    extra = 0


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "user", "created_at")
    search_fields = ("name", "email", "phone", "skills__name")
    list_filter = ("created_at",)
    inlines = [EducationInline, ExperienceInline, SkillInline, CertificationInline]


@admin.register(UploadedResume)
class UploadedResumeAdmin(admin.ModelAdmin):
    list_display = ("original_filename", "user", "status", "uploaded_at", "parsed_at")
    list_filter = ("status",)
    search_fields = ("original_filename",)
