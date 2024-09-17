from django.db import models
from django.utils import timezone
from django_fsm import FSMField, transition

from ..clients.models import Client
from ..products.models import Product


class OrdersManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at=None)


class Orders(models.Model):
    code = models.CharField(max_length=15, unique=True)
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
