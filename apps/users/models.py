from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

from apps.company.models import Company


class CustomUser(AbstractUser):

    DEPARTMENT_CHOICES = [
        ("", "Select Department"),
        ("Purchasing", "Purchasing"),
        ("Inventory", "Inventory"),
        ("HR", "Human Resources"),
    ]

    POSITION_CHOICES = [
        ("", "Select Position"),
        ("Intern", "Intern"),
        ("Specialist", "Specialist"),
        ("Manager", "Manager"),
        ("BOSS", "BOSS"),
    ]

    email = models.EmailField(unique=True)
    birthday = models.DateField(blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.CharField(max_length=100, blank=False, null=False, default="")
    company = models.ForeignKey(
        Company, on_delete=models.PROTECT, related_name="CustomUser", default=0
    )
    department = models.CharField(
        choices=DEPARTMENT_CHOICES, max_length=20, default="", blank=False, null=False
    )
    position = models.CharField(
        choices=POSITION_CHOICES, max_length=20, default="", blank=False, null=False
    )
    hire_date = models.DateTimeField(default=timezone.now)
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.username}"

    class Meta:

        permissions = [
            # 設置權限類別
            ("can_edit_department", "Can edit department"),
            ("can_edit_position", "Can edit position"),
            ("can_edit_hire_date", "Can edit hire date"),
        ]
