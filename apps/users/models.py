from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class CustomUser(AbstractUser):

    # 名稱、電話、地址、email、帳號、密碼、職稱、入職時間、備註
    phone = models.CharField(max_length=10, blank=True, null=True)
    address = models.CharField(max_length=100, blank=True, null=True)
    title = models.CharField(max_length=100, blank=True, null=True)
    hire_date = models.DateTimeField(blank=True, null=True, default=timezone.now)
    note = models.TextField(blank=True, null=True)
    password1 = models.CharField(max_length=100, blank=True, null=True)
    password2 = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.username}"
