from django.db import models


# Create your models here.
class Supplier(models.Model):
    name = models.CharField(max_length=100)
    tel = models.CharField(max_length=20)
    contact = models.CharField(max_length=100)
    GUInumber = models.IntegerField(unique=True)
    address = models.TextField()
    remark = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.GUInumber})"
