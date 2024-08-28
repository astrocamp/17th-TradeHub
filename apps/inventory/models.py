from django.db import models
from products.models import Product
from suppliers.models import Supplier


class Inventory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT)
    quantity = models.IntegerField()
    safety_stock = models.IntegerField()
    last_updated = models.DateTimeField(auto_now=True)
    note = models.TextField(blank=True)

    def __str__(self):
        return f"{self.product_name}"
