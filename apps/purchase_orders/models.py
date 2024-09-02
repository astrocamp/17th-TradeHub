from django.db import models
from django.utils import timezone

from apps.suppliers.models import Supplier

# Import Supplier model from the suppliers app


class PurchaseOrder(models.Model):
    order_number = models.CharField(max_length=20, unique=True)
    supplier = models.ForeignKey(
        Supplier, on_delete=models.CASCADE, related_name="purchase_orders"
    )
    order_date = models.DateField(default=timezone.now)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"PO {self.order_number} - {self.supplier.name}"
