from django.db import models
from django.utils import timezone

from apps.suppliers.models import Supplier


class PurchaseOrder(models.Model):
    order_number = models.CharField(max_length=20, unique=True, editable=False)
    supplier = models.ForeignKey(
        Supplier, on_delete=models.CASCADE, related_name="purchase_orders"
    )
    supplier_tel = models.CharField(max_length=20, blank=True, null=True)
    contact_person = models.CharField(max_length=100, blank=True, null=True)
    supplier_email = models.EmailField(blank=True, null=True)
    order_date = models.DateField(default=timezone.now)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.order_number:
            today = timezone.now().strftime("%Y%m%d")
            last_order = (
                PurchaseOrder.objects.filter(order_number__startswith=today)
                .order_by("order_number")
                .last()
            )
            if last_order:
                last_order_number = int(last_order.order_number[-3:])
                new_order_number = f"{last_order_number + 1:03d}"
            else:
                # If this is the first order of the day, start with 001
                new_order_number = "001"
            self.order_number = f"{today}{new_order_number}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"PO {self.order_number} - {self.supplier.name}"
