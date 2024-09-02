from django.db import models

from apps.suppliers.models import Supplier

# Create your models here.


class Product(models.Model):
    product_id = models.CharField(max_length=10)
    product_name = models.CharField(max_length=20)
    price = models.IntegerField(null=False, blank=False)
    supplier = models.ManyToManyField(Supplier, related_name="products")
    productNumber = models.CharField(max_length=10)
    title = models.CharField(max_length=20)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    note = models.TextField()
