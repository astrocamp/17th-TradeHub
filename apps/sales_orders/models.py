from django.db import models
from django.utils import timezone
from django_fsm import FSMField, transition

from apps.clients.models import Client
from apps.inventory.models import Inventory
from apps.products.models import Product


class SalesOrderManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at=None)


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
    deleted_at = models.DateTimeField(null=True)

    objects = SalesOrderManager()

    def delete(self):
        self.deleted_at = timezone.now()
        self.save()

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
