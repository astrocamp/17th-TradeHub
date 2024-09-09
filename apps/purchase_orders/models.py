from django.db import models
from django.utils import timezone

from apps.products.models import Product
from apps.suppliers.models import Supplier


class PurchaseOrder(models.Model):
    order_number = models.CharField(max_length=20, unique=True, editable=False)
    supplier = models.ForeignKey(
        Supplier, on_delete=models.CASCADE, related_name="purchase_orders"
    )
    supplier_tel = models.CharField(max_length=20, blank=True, null=True)
    contact_person = models.CharField(max_length=100, blank=True, null=True)
    supplier_email = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    total_amount = models.PositiveIntegerField()
    notes = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.order_number:
            today = timezone.localtime().strftime("%Y%m%d")
            last_order = (
                PurchaseOrder.objects.filter(order_number__startswith=today)
                .order_by("order_number")
                .last()
            )
            if last_order:
                last_order_number = int(last_order.order_number[-3:])
                new_order_number = f"{last_order_number + 1:03d}"
            else:
                new_order_number = "001"
            self.order_number = f"{today}{new_order_number}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"PO {self.order_number} - {self.supplier.name}"


class ProductItem(models.Model):
    purchase_order = models.ForeignKey(
        "PurchaseOrder", on_delete=models.CASCADE, related_name="items"
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.PositiveIntegerField()
    subtotal = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.product} - {self.quantity} @ {self.price}"
