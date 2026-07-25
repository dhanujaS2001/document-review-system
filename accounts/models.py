from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = (
        ("AUTHOR", "Author"),
        ("REVIEWER", "Reviewer"),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    prefix = models.CharField(max_length=3, unique=True)

    def __str__(self):
        return self.get_full_name() or self.username