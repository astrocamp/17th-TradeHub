from django.db import models
from django.utils import timezone
from django_fsm import FSMField, transition

from apps.company.models import Company
from apps.suppliers.models import Supplier
from apps.users.models import CustomUser


class ProductManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at=None)


class Product(models.Model):
    number = models.CharField(max_length=20)
    product_name = models.CharField(max_length=20)
    cost_price = models.PositiveIntegerField()
    sale_price = models.PositiveIntegerField()
    supplier = models.ForeignKey(
        Supplier, on_delete=models.PROTECT, related_name="products", default=0
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        related_name="products",
        blank=True,
        null=True,
    )
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, blank=True, null=True
    )
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = ProductManager()

    def delete(self):
        self.deleted_at = timezone.now()
        self.save()

    def __str__(self):
        return self.product_name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.number = f"I{self.id:03d}"
        super().save(update_fields=["number"])

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
