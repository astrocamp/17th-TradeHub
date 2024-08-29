from django.db import models

# from suppliers.models import Supplier
# from products.models import Product


class Inventory(models.Model):
    # product = models.ForeignKey(Product, on_delete=models.PROTECT)
    # supplie = models.ForeignKey(Supplier, on_delete=models.PROTECT)
    quantity = models.IntegerField()
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product_name}"
