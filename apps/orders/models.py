from django.db import models
from django.utils import timezone
from django_fsm import FSMField, transition

from apps.company.models import Company

from ..clients.models import Client
from ..inventory.models import Inventory
from ..products.models import Product


class OrdersManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at=None)


class Orders(models.Model):
    code = models.CharField(max_length=15, unique=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="orders")
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name="orders"
    )
    price = models.PositiveIntegerField(blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)
    stock_quantity = models.ForeignKey(
        Inventory, on_delete=models.CASCADE, related_name="orders"
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        related_name="orders",
        blank=True,
        null=True,
    )
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = OrdersManager()

    is_finished = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.stock_quantity = Inventory.objects.get(product=self.product)
        super().save(*args, **kwargs)

    def delete(self):
        self.deleted_at = timezone.now()
        self.save()

    TO_BE_CONFIRMED = "to_be_confirmed"
    PROGRESS = "progress"
    FINISHED = "finished"

    AVAILABLE_STATES = TO_BE_CONFIRMED, PROGRESS, FINISHED

    STATES_CHOICES = [
        (TO_BE_CONFIRMED, "待確認"),
        (PROGRESS, "進行中"),
        (FINISHED, "已完成"),
    ]

    state = FSMField(
        default=TO_BE_CONFIRMED,
        choices=STATES_CHOICES,
        protected=True,
    )

    @transition(field=state, source="*", target=TO_BE_CONFIRMED)
    def set_to_be_confirmed(self):
        pass

    @transition(field=state, source="*", target=PROGRESS)
    def set_progress(self):
        pass

    @transition(field=state, source="*", target=FINISHED)
    def set_finished(self):
        pass
