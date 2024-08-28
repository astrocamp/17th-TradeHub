from django.db import models

# Create your models here.


class Product(models.Model):
    productNumber = models.CharField(max_length=10)
    title = models.CharField(max_length=20)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    note = models.TextField()
