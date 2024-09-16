from django.db import models
from django_fsm import FSMField, transition

from apps.suppliers.models import Supplier


class Product(models.Model):
    product_id = models.CharField(max_length=10, unique=True)
    product_name = models.CharField(max_length=20)
    cost_price = models.PositiveIntegerField()
    sale_price = models.PositiveIntegerField()
    supplier = models.ForeignKey(
        Supplier, on_delete=models.PROTECT, related_name="products", default=0
    )
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.product_name

    PRODUCT_STATE_OFTEN = "often"
    PRODUCT_STATE_HAPLY = "haply"
    PRODUCT_STATE_NEVER = "never"

    PRODUCT_STATE_CHOICES = [
        (PRODUCT_STATE_OFTEN, "經常"),
        (PRODUCT_STATE_HAPLY, "偶爾"),
        (PRODUCT_STATE_NEVER, "從不"),
    ]

    state = FSMField(
        default=PRODUCT_STATE_OFTEN,
        choices=PRODUCT_STATE_CHOICES,
        protected=True,
    )

    def update_state(self):
        pass

    @transition(field=state, source="*", target=PRODUCT_STATE_NEVER)
    def set_never(self):
        pass

    @transition(field=state, source="*", target=PRODUCT_STATE_HAPLY)
    def set_haply(self):
        pass

    @transition(field=state, source="*", target=PRODUCT_STATE_OFTEN)
    def set_often(self):
        pass

    def add_state(self):
        pass

    def remove_state(self):
        pass
