from django.db import models
from django_fsm import FSMField, transition

from apps.company.models import Company
from apps.suppliers.models import Supplier


class Product(models.Model):
    product_number = models.CharField(max_length=10, unique=True)
    product_name = models.CharField(max_length=20)
    cost_price = models.PositiveIntegerField()
    sale_price = models.PositiveIntegerField()
    supplier = models.ForeignKey(
        Supplier, on_delete=models.PROTECT, related_name="products", default=0
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        related_name="Product",
        blank=True,
        null=True,
    )
    note = models.TextField(blank=True, null=True)

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
