from django.db import models

# Create your models here.


class Product(models.Model):
    productNumber = models.CharField(max_length=10)
    title = models.CharField(max_length=20)
    price = models.IntegerField()
    quantity = models.IntegerField()
    note = models.TextField()
