import re

from django.db import models
from django.utils import timezone
from django_fsm import FSMField, transition

from apps.clients.models import Client
from apps.company.models import Company
from apps.inventory.models import Inventory
from apps.products.models import Product


class SalesOrderManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at=None)


class SalesOrder(models.Model):
    order_number = models.CharField(max_length=11, unique=True)
    client = models.ForeignKey(
        Client, on_delete=models.PROTECT, related_name="sales_orders"
    )
    client_tel = models.CharField(max_length=15)
    client_address = models.CharField(max_length=150)
    client_email = models.EmailField(unique=False)
    amount = models.PositiveIntegerField()
    username = models.CharField(max_length=150, default="admin")
    note = models.TextField(blank=True, null=True)
    company = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        related_name="sales_orders",
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    RECEIVING_METHOD_CHOICES = [
        ("貨運", "貨運"),
        ("自取", "自取"),
    ]
    shipping_method = models.CharField(max_length=20, choices=RECEIVING_METHOD_CHOICES)

    objects = SalesOrderManager()
    all_objects = models.Manager()

    is_finished = models.BooleanField(default=False)

    is_finished = models.BooleanField(default=False)

    def delete(self):
        self.deleted_at = timezone.now()
        self.save()

    def __repr__(self):
        return f"銷貨單:{self.order_number} - 客戶:{self.client.name}"

    def format_client_tel(self, number):
        number = re.sub(r"\D", "", number)
        if len(number) == 10 and number.startswith("09"):
            return f"{number[:4]}-{number[4:]}"
        elif len(number) == 9 and number.startswith("0"):
            return f"{number[:2]}-{number[2:]}"
        else:
            return number

    def __str__(self):
        return self.product.product_name

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


class SalesOrderProductItem(models.Model):
    sales_order = models.ForeignKey(
        "SalesOrder", on_delete=models.CASCADE, related_name="items"
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    stock_quantity = models.ForeignKey(
        Inventory, on_delete=models.PROTECT, related_name="sales_orders"
    )
    ordered_quantity = models.PositiveIntegerField()
    shipped_quantity = models.PositiveIntegerField()
    sale_price = models.PositiveIntegerField()
    subtotal = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.product} - {self.shipped_quantity} @ {self.sale_price}"
