from django.db import models
from django.utils import timezone
from django_fsm import FSMField, transition

from ..clients.models import Client
from ..products.models import Product


class OrdersManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at=None)


class Orders(models.Model):
    code = models.CharField(max_length=15)
    client = models.ForeignKey(Client, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = OrdersManager()

    def delete(self):
        self.deleted_at = timezone.now()
        self.save()

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
