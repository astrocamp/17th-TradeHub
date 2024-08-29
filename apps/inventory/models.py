from django.db import models

from apps.products.models import Product

# from apps.suppliers.models import Supplier


class Inventory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    # supplier = ForeignKey(Supplier, on_delete=models.PROTECT)
    quantity = models.IntegerField(null=False, blank=False)
    safety_stock = models.IntegerField(null=True, blank=False)
    last_updated = models.DateTimeField(auto_now=True)
    note = models.TextField(blank=True)

    def __str__(self):
        return self.product
