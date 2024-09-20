from django.db import models
from django.utils import timezone
from django_fsm import FSMField, transition

from apps.products.models import Product
from apps.suppliers.models import Supplier


class GoodReceiptManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at=None)


class GoodsReceipt(models.Model):
    receipt_number = models.CharField(unique=True, max_length=10)
    supplier = models.ForeignKey(
        Supplier, on_delete=models.PROTECT, related_name="goods_receipts"
    )
    goods_name = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name="goods_receipts"
    )
    order_quantity = models.PositiveIntegerField()
    purchase_quantity = models.PositiveIntegerField(null=True)
    method = models.CharField(max_length=20)
    date = models.DateField(default=timezone.now)
    note = models.TextField()
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = GoodReceiptManager()

    def delete(self):
        self.deleted_at = timezone.now()
        self.save()

    def __repr__(self):
        return f"{self.receipt_number}-{self.supplier.name}-{self.goods_name}"

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
