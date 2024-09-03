from datetime import date

from django.db import models


class Supplier(models.Model):
    name = models.CharField(max_length=100, blank=True)
    telephone = models.CharField(max_length=10, blank=True, null=False)
    contact_person = models.CharField(max_length=100, blank=False, null=False)
    email = models.CharField(max_length=254, blank=True, null=False)
    gui_number = models.CharField(max_length=8, unique=True, blank=True, null=False)
    address = models.TextField(blank=True, null=False)
    established_date = models.DateField(default=date.today)
    note = models.TextField(blank=True, null=False)

    def __str__(self):
        return f"{self.name} ({self.gui_number})"
