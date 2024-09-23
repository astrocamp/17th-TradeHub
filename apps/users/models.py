import re

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

from apps.company.models import Company


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

class CustomUser(AbstractUser):

    email = models.EmailField(unique=True)
    birthday = models.DateField(blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=False)
    address = models.CharField(max_length=100, blank=False, null=False, default="")
    company = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        related_name="CustomUser",
        blank=True,
        null=True,
    )
    department = models.CharField(
        choices=DEPARTMENT_CHOICES, max_length=20, default="", blank=False, null=False
    )
    position = models.CharField(
        choices=POSITION_CHOICES, max_length=20, default="", blank=False, null=False
    )
    hire_date = models.DateTimeField(default=timezone.now)
    note = models.TextField(blank=True, null=False)
    is_superuser = models.BooleanField(default=False)
    first_login = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.username}"

    def get_full_name(self):
        return f"{self.last_name} {self.first_name}"

    def format_telephone(self, number):
        number = re.sub(r"\D", "", number)

        # 將輸入的電話號碼格式化為 09XX-XXXXXX 或 0X-XXXXXXX
        if len(number) == 10 and number.startswith("09"):
            return f"{number[:4]}-{number[4:]}"
        elif len(number) == 10 and number.startswith(("037", "049")):
            return f"{number[:3]}-{number[3:]}"
        elif len(number) == 10:
            return f"{number[:2]}-{number[2:]}"
        elif len(number) == 9 and number.startswith("0"):
            return f"{number[:2]}-{number[2:]}"
        else:
            return number
