from django.contrib import admin
from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "project_code",
        "project_name",
        "uploaded_by",
        "reviewed_by",
        "status",
        "given_to",
        "created_at",
        "updated_at",
    )

    list_filter = (
        "status",
        "uploaded_by",
        "reviewed_by",
        "created_at",
    )

    search_fields = (
        "project_code",
        "project_name",
        "description",
        "given_to",
    )

    readonly_fields = (
        "project_code",
        "created_at",
        "updated_at",
    )

    ordering = ("-created_at",)