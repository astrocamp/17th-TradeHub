from django.db import models


# Create your models here.
class Client(models.Model):
    name = models.CharField(max_length=30)
    phone_number = models.CharField(max_length=15)
    address = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    delete_at = models.DateTimeField(auto_now=True)
    note = models.TextField(null=True, max_length=150)

    def __str__(self):
        return self.name
