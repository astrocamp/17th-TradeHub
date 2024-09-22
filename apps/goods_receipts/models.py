import re

from django.db import models
from django.utils import timezone
from django_fsm import FSMField, transition

from apps.company.models import Company
from apps.products.models import Product
from apps.suppliers.models import Supplier


class GoodReceiptManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at=None)


class GoodsReceipt(models.Model):
    order_number = models.CharField(max_length=11)
    supplier = models.ForeignKey(
        Supplier, on_delete=models.PROTECT, related_name="goods_receipts"
    )
    supplier_tel = models.CharField(max_length=15)
    contact_person = models.CharField(max_length=20)
    supplier_email = models.EmailField(unique=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    amount = models.PositiveIntegerField()
    company = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        related_name="goods_receipts",
        blank=True,
        null=True,
    )
    note = models.TextField(blank=True, null=True)
    username = models.CharField(max_length=150, default="admin")
    RECEIVING_METHOD_CHOICES = [
        ("貨運", "貨運"),
        ("自取", "自取"),
    ]
    receiving_method = models.CharField(max_length=20, choices=RECEIVING_METHOD_CHOICES)

    objects = GoodReceiptManager()
    all_objects = models.Manager()

    def delete(self):
        self.deleted_at = timezone.now()
        self.save()

    def __repr__(self):
        return f"{self.order_number} - {self.supplier.name}"

    def format_supplier_tel(self, number):
        number = re.sub(r"\D", "", number)
        if len(number) == 10 and number.startswith("09"):
            return f"{number[:4]}-{number[4:]}"
        elif len(number) == 9 and number.startswith("0"):
            return f"{number[:2]}-{number[2:]}"
        else:
            return number

    TO_BE_RESTOCKED = "to_be_restocked"
    TO_BE_STOCKED = "to_be_stocked"
    FINISHED = "finished"

    AVAILABLE_STATES = TO_BE_RESTOCKED, TO_BE_STOCKED, FINISHED

    STATES_CHOICES = [
        (TO_BE_RESTOCKED, "待進貨"),
        (TO_BE_STOCKED, "待入庫"),
        (FINISHED, "完成"),
    ]

    state = FSMField(
        default=TO_BE_RESTOCKED,
        choices=STATES_CHOICES,
        protected=True,
    )

    is_finished = models.BooleanField(default=False)

    @transition(field=state, source="*", target=TO_BE_RESTOCKED)
    def set_to_be_restocked(self):
        pass

    @transition(field=state, source="*", target=TO_BE_STOCKED)
    def set_to_be_stocked(self):
        pass

    @transition(field=state, source="*", target=FINISHED)
    def set_finished(self):
        self.is_finished = False


class GoodsReceiptProductItem(models.Model):
    goods_receipt = models.ForeignKey(
        "GoodsReceipt", on_delete=models.CASCADE, related_name="items"
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    ordered_quantity = models.PositiveIntegerField()
    received_quantity = models.PositiveIntegerField()
    cost_price = models.PositiveIntegerField()
    subtotal = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.product} - {self.received_quantity} @ {self.cost_price}"
