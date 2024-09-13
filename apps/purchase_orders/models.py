import re

from django.db import models
from django.utils import timezone
from django_fsm import FSMField, transition

from apps.products.models import Product
from apps.suppliers.models import Supplier


class PurchaseOrderManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at=None)


class PurchaseOrder(models.Model):
    order_number = models.CharField(max_length=11)
    supplier = models.ForeignKey(
        Supplier, on_delete=models.PROTECT, related_name="purchase_orders"
    )
    supplier_tel = models.CharField(max_length=15)
    contact_person = models.CharField(max_length=20)
    supplier_email = models.EmailField(unique=False)
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    total_amount = models.PositiveIntegerField()
    notes = models.TextField(blank=True, null=True)

    objects = PurchaseOrderManager()

    def delete(self):
        self.deleted_at = timezone.now()
        self.save()

    def __repr__(self):
        return f"{self.order_number} - {self.supplier.name}"

    def format_supplier_tel(self, number):
        # 把所有非數字符號改為空字串(清除)
        number = re.sub(r"\D", "", number)

        # 將輸入的電話號碼格式化為 09XX-XXXXXX 或 0X-XXXXXXX
        if len(number) == 10 and number.startswith("09"):
            return f"{number[:4]}-{number[4:]}"
        elif len(number) == 9 and number.startswith("0"):
            return f"{number[:2]}-{number[2:]}"
        else:
            return number

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


class ProductItem(models.Model):
    purchase_order = models.ForeignKey(
        "PurchaseOrder", on_delete=models.CASCADE, related_name="items"
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.PositiveIntegerField()
    subtotal = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.product} - {self.quantity} @ {self.price}"
