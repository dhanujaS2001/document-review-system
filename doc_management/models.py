import os
from django.db import models
from django.conf import settings

def generate_project_code(user):

    prefix = user.prefix.upper()

    latest = (
        Project.objects.filter(uploaded_by=user)
        .order_by("-id")
        .first()
    )

    if latest:
        number = int(latest.project_code[3:])
        number += 1
    else:
        number = 1

    return f"{prefix}{number:04d}"

def generate_review_code(doc_obj):
    return f"RE_{doc_obj.project_code}"


def review_upload_path(instance, filename):
    extension = filename.split(".")[-1]
    review_code = generate_review_code(instance)
    return f"reviews/{review_code}.{extension}"

def project_upload_path(instance, filename):

    extension = filename.split(".")[-1]

    return f"projects/{instance.project_code}.{extension}"


def review_upload_path(instance, filename):
    print(instance)
    extension = filename.split(".")[-1]

    reviewer = instance.reviewed_by.prefix

    filename = generate_review_code(instance)

    return f"reviews/{filename}.{extension}"

class Project(models.Model):

    STATUS_CHOICES = (
        ("READY", "Ready For Review"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
        ("CHANGES", "Needs Changes"),
    )

    project_code = models.CharField(max_length=10, unique=True)

    project_name = models.CharField(max_length=200)

    description = models.TextField()

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="projects_uploaded"
    )

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="projects_reviewed"
    )

    project_document = models.FileField(
        upload_to=project_upload_path
    )

    review_document = models.FileField(
        upload_to=review_upload_path,
        blank=True,
        null=True
    )

    review_description = models.TextField(
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="READY"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)
    given_to = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Name of the student the approved project was given to"
    )
    leaner_no = models.CharField(max_length=200,
            blank=True,
            null=True)
    

    def __str__(self):
        return self.project_code


def replace_file(field, new_file):

    if field:

        if os.path.isfile(field.path):
            os.remove(field.path)

    field.save(new_file.name, new_file, save=False)