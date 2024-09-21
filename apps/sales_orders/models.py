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
    note = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)

    objects = SalesOrderManager()

    is_finished = models.BooleanField(default=False)

    def delete(self):
        self.deleted_at = timezone.now()
        self.save()

    def __repr__(self):
        return f"訂單 #{self.id} - 客戶: {self.client.name} ({self.created_at.date()})"

    PENDING = "pending"
    PROGRESS = "progress"
    FINISHED = "finished"

    AVAILABLE_STATES = PENDING, PROGRESS, FINISHED

    STATES_CHOICES = [
        (PENDING, "待處理"),
        (PROGRESS, "進行中"),
        (FINISHED, "已完成"),
    ]

    state = FSMField(
        default=PROGRESS,
        choices=STATES_CHOICES,
        protected=True,
    )

    @transition(field=state, source="*", target=PENDING)
    def set_pending(self):
        pass

    @transition(field=state, source="*", target=PROGRESS)
    def set_progress(self):
        pass

    @transition(field=state, source="*", target=FINISHED)
    def set_finished(self):
        pass
