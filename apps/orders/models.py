import re

from django.db import models
from django.utils import timezone
from django_fsm import FSMField, transition

from apps.clients.models import Client
from apps.products.models import Product


class OrdersManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at=None)


class Order(models.Model):
    order_number = models.CharField(max_length=11, unique=True)
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name="orders")
    client_tel = models.CharField(max_length=15)
    client_address = models.CharField(max_length=150)
    client_email = models.EmailField(unique=False)
    amount = models.PositiveIntegerField()
    username = models.CharField(max_length=150, default="admin")
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = OrdersManager()
    all_objects = models.Manager()

    def delete(self):
        self.deleted_at = timezone.now()
        self.save()

    def __repr__(self):
        return f"{self.order_number} - {self.client.name}"

    def format_client_tel(self, number):
        number = re.sub(r"\D", "", number)
        if len(number) == 10 and number.startswith("09"):
            return f"{number[:4]}-{number[4:]}"
        elif len(number) == 9 and number.startswith("0"):
            return f"{number[:2]}-{number[2:]}"
        else:
            return number

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


class OrderProductItem(models.Model):
    order = models.ForeignKey("Order", on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    ordered_quantity = models.PositiveIntegerField()
    sale_price = models.PositiveIntegerField()
    subtotal = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.product} - {self.quantity} @ {self.sale_price}"
