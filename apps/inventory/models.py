from django.db import models
from django_fsm import FSMField, transition

from apps.products.models import Product
from apps.suppliers.models import Supplier


class Inventory(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name="inventories"
    )
    supplier = models.ForeignKey(
        Supplier, on_delete=models.PROTECT, related_name="inventories"
    )
    quantity = models.IntegerField(null=False, blank=False)
    safety_stock = models.IntegerField(null=True, blank=False)
    last_updated = models.DateTimeField(auto_now=True)
    note = models.TextField(blank=True)

    def __str__(self):
        return f"{self.product} - {self.get_state_display()} ({self.quantity})"

    STOCK_STATE_OUT = "out_stock"
    STOCK_STATE_LOW = "low_stock"
    STOCK_STATE_NORMAL = "normal"

    STOCK_STATE_CHOICES = [
        (STOCK_STATE_OUT, "缺貨"),
        (STOCK_STATE_LOW, "低於安全庫存量"),
        (STOCK_STATE_NORMAL, "正常"),
    ]

    state = FSMField(
        default=STOCK_STATE_NORMAL,
        choices=STOCK_STATE_CHOICES,
        protected=True,
    )

    def update_state(self):
        if self.quantity <= 0:
            self.set_out_stock()
        elif self.quantity < self.safety_stock:
            self.set_low_stock()
        else:
            self.set_normal()
        self.save()

    @transition(field=state, source="*", target=STOCK_STATE_OUT)
    def set_out_stock(self):
        # 缺貨時的邏輯
        pass

    @transition(field=state, source="*", target=STOCK_STATE_LOW)
    def set_low_stock(self):
        # 低於安全庫存量時的邏輯
        pass

    @transition(field=state, source="*", target=STOCK_STATE_NORMAL)
    def set_normal(self):
        # 庫存正常時的邏輯
        pass

    def add_stock(self, amount):
        self.quantity += amount
        self.update_state()

    def remove_stock(self, amount):
        self.quantity = max(0, self.quantity - amount)
        self.update_state()
