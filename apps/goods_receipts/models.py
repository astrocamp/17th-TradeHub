from django.db import models
from django.utils import timezone

from apps.products.models import Product
from apps.suppliers.models import Supplier


class GoodReceiptManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at=None)


class GoodsReceipt(models.Model):
    receipt_number = models.CharField(unique=True, max_length=10)
    supplier = models.ForeignKey(
        Supplier, on_delete=models.PROTECT, related_name="goods_receipts"
    )
    goods_name = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name="goods_receipts"
    )
    quantity = models.PositiveIntegerField()
    method = models.CharField(max_length=20)
    date = models.DateField(default=timezone.now)
    note = models.TextField()
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = GoodReceiptManager()

    def delete(self):
        self.deleted_at = timezone.now()
        self.save()

    def __str__(self):
        return f"{self.receipt_number} - {self.supplier.name} - {self.goods_name}"
