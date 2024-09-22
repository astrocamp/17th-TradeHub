from django.db import models
from django.utils import timezone
from django_fsm import FSMField, transition

from apps.suppliers.models import Supplier


class ProductManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at=None)


class Product(models.Model):
    number = models.CharField(max_length=20, unique=True)
    product_name = models.CharField(max_length=20)
    cost_price = models.PositiveIntegerField()
    sale_price = models.PositiveIntegerField()
    supplier = models.ForeignKey(
        Supplier, on_delete=models.PROTECT, related_name="products", default=0
    )
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True)

    objects = ProductManager()

    def delete(self):
        self.deleted_at = timezone.now()
        self.save()

    def __str__(self):
        return self.product_name

    OFTEN = "often"
    HAPLY = "haply"
    NEVER = "never"

    STATE_CHOICES = [
        (OFTEN, "經常購買"),
        (HAPLY, "偶爾購買"),
        (NEVER, "未購買"),
    ]

    state = FSMField(
        default=NEVER,
        choices=STATE_CHOICES,
        protected=True,
    )

    @transition(field=state, source="*", target=NEVER)
    def set_never(self):
        pass

    @transition(field=state, source="*", target=HAPLY)
    def set_haply(self):
        pass

    @transition(field=state, source="*", target=OFTEN)
    def set_often(self):
        pass
