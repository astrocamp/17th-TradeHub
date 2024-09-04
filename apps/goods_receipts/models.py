from django.db import models
from django.utils import timezone

from apps.suppliers.models import Supplier

# Create your models here.


class GoodsReceipt(models.Model):
    receipt_number = models.CharField(max_length=10)
    supplier = models.ForeignKey(
        Supplier, on_delete=models.CASCADE, related_name="goods_receipts"
    )
    goods_name = models.CharField(max_length=20)
    quantity = models.IntegerField()
    method = models.CharField(max_length=20)
    date = models.DateField(default=timezone.now)
    note = models.TextField()

    def __str__(self):
        return f"GR {self.receipt_number} - {self.supplier.name}"
