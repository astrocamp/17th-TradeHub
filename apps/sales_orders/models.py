from django.db import models
from django_fsm import FSMField, transition

from apps.clients.models import Client
from apps.inventory.models import Inventory
from apps.products.models import Product


class SalesOrder(models.Model):
    client = models.ForeignKey(
        Client, on_delete=models.PROTECT, related_name="sales_orders"
    )
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name="sales_orders"
    )
    quantity = models.PositiveIntegerField()
    stock = models.ForeignKey(
        Inventory, on_delete=models.PROTECT, related_name="sales_orders"
    )
    price = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"訂單 #{self.id} - 客戶: {self.client.name} ({self.created_at.date()})"

    STOCK_STATE_ABNORMAL = "unfinish"
    STOCK_STATE_NORMAL = "finish"

    STOCK_STATE_CHOICES = [
        (STOCK_STATE_ABNORMAL, "未完成"),
        (STOCK_STATE_NORMAL, "完成"),
    ]

    state = FSMField(
        default=STOCK_STATE_ABNORMAL,
        choices=STOCK_STATE_CHOICES,
        protected=True,
    )

    def update_state(self):
        if self.quantity > self.stock.quantity:
            self.set_abnormal()
        else:
            self.set_normal()
        self.save()

    @transition(field=state, source="*", target=STOCK_STATE_ABNORMAL)
    def set_abnormal(self):
        pass

    @transition(field=state, source="*", target=STOCK_STATE_NORMAL)
    def set_normal(self):
        pass

    def add_order(self, amount):
        pass

    def remove_order(self, amount):
        pass
