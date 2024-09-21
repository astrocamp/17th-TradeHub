from django.db import models


class Company(models.Model):
    company_id = models.CharField(max_length=20)
    company_name = models.CharField(max_length=30)
    gui_number = models.CharField(max_length=8, unique=True)
    address = models.CharField(max_length=50, blank=False, null=False, default="")
    user = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
