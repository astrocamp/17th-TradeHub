from django.db import models, transaction
from django.utils import timezone
from django_fsm import FSMField, transition

from apps.company.models import Company
from apps.products.models import Product
from apps.suppliers.models import Supplier
from apps.users.models import CustomUser


class InventoryManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at=None)


class Inventory(models.Model):
    number = models.CharField(max_length=20, unique=True)
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name="inventories"
    )
    supplier = models.ForeignKey(
        Supplier, on_delete=models.PROTECT, related_name="inventories"
    )
    quantity = models.PositiveIntegerField()
    safety_stock = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    company = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        related_name="inventories",
        blank=True,
        null=True,
    )
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, blank=True, null=True
    )
    deleted_at = models.DateTimeField(null=True)
    note = models.TextField(blank=True)

    objects = InventoryManager()

    def delete(self):
        self.deleted_at = timezone.now()
        self.save()

    def __str__(self):
        return f"{self.quantity}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.number = f"P{self.id:03d}"
        super().save(*args, update_fields=["number"])

    OUT_STOCK = "out_stock"
    LOW_STOCK = "low_stock"
    NORMAL = "normal"
    NEW_STOCK = "new_stock"

    AVAILABLE_STATES = OUT_STOCK, LOW_STOCK, NORMAL

    STATES_CHOICES = [
        (OUT_STOCK, "缺貨"),
        (LOW_STOCK, "低於安全庫存量"),
        (NORMAL, "正常"),
        (NEW_STOCK, "新庫存"),
    ]

    state = FSMField(
        default=NORMAL,
        choices=STATES_CHOICES,
        protected=True,
    )

    @transition(field=state, source="*", target=OUT_STOCK)
    def set_out_stock(self):
        pass

    @transition(field=state, source="*", target=LOW_STOCK)
    def set_low_stock(self):
        pass

    @transition(field=state, source="*", target=NORMAL)
    def set_normal(self):
        pass

    @transition(field=state, source="*", target=NEW_STOCK)
    def set_new_stock(self):
        pass
