from django.db import models
from django.utils import timezone
from django_fsm import FSMField, transition

from apps.products.models import Product
from apps.suppliers.models import Supplier

# Create your models here.


class GoodsReceipt(models.Model):
    receipt_number = models.CharField(max_length=10)
    supplier = models.ForeignKey(
        Supplier, on_delete=models.CASCADE, related_name="goods_receipts"
    )
    goods_name = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="goods_receipts"
    )
    quantity = models.IntegerField()
    method = models.CharField(max_length=20)
    date = models.DateField(default=timezone.now)
    note = models.TextField()

    def __repr__(self):
        return f"GR {self.receipt_number} - {self.supplier.name} - {self.goods_name}"

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

    def check_receipt_state(self):
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
