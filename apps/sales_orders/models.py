from django.db import models
from django_fsm import FSMField, transition

from apps.clients.models import Client
from apps.inventory.models import Inventory
from apps.products.models import Product


class SalesOrder(models.Model):
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name="sales_orders"
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="sales_orders"
    )
    quantity = models.PositiveIntegerField()
    stock = models.ForeignKey(
        Inventory, on_delete=models.CASCADE, related_name="sales_orders"
    )
    price = models.DecimalField(max_digits=10, decimal_places=0)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __repr__(self):
        return f"訂單 #{self.id} - 客戶: {self.client.name} ({self.created_at.date()})"

    UNFINISH = "unfinish"
    FINISHED = "finished"

    AVAILABLE_STATES = UNFINISH, FINISHED

    AVAILABLE_STATES_CHOICES = [
        (UNFINISH, "未完成"),
        (FINISHED, "完成"),
    ]

    state = FSMField(
        default=UNFINISH,
        choices=AVAILABLE_STATES_CHOICES,
        protected=True,
    )

    def check_order_state(self):
        if self.quantity < self.stock.quantity:
            self.set_unfinish()
        else:
            self.set_finished()
        self.save()

    @transition(field=state, source="*", target=UNFINISH)
    def set_unfinish(self):
        pass

    @transition(field=state, source="*", target=FINISHED)
    def set_finished(self):
        pass
