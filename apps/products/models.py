from django.db import models

from apps.suppliers.models import Supplier

# Create your models here.


class Product(models.Model):
    product_id = models.CharField(max_length=10, unique=True)
    product_name = models.CharField(max_length=20)
    price = models.PositiveIntegerField(null=False, blank=False)
    supplier = models.ForeignKey(
        Supplier, on_delete=models.CASCADE, related_name="products", default=0
    )
    note = models.TextField()

    def __str__(self):
        return self.product_name
