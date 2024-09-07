from django.db import models
from django.utils import timezone
from django_fsm import FSMField, transition


class Supplier(models.Model):
    name = models.CharField(max_length=100, blank=True)
    telephone = models.CharField(max_length=10, blank=True, null=False)
    contact_person = models.CharField(max_length=100, blank=False, null=False)
    email = models.CharField(max_length=254, blank=True, null=False)
    gui_number = models.CharField(max_length=8, unique=True, blank=True, null=False)
    address = models.TextField(blank=True, null=False)
    established_date = models.DateTimeField(default=timezone.now)
    note = models.TextField(blank=True, null=False)

    def __str__(self):
        return f"{self.name} ({self.gui_number})"

    SUPPLIER_STATE_OFTEN = "often"
    SUPPLIER_STATE_HAPLY = "haply"
    SUPPLIER_STATE_NEVER = "never"

    SUPPLIER_STATE_CHOICES = [
        (SUPPLIER_STATE_OFTEN, "經常"),
        (SUPPLIER_STATE_HAPLY, "偶爾"),
        (SUPPLIER_STATE_NEVER, "從不"),
    ]

    state = FSMField(
        default=SUPPLIER_STATE_NEVER,
        choices=SUPPLIER_STATE_CHOICES,
        protected=True,
    )

    def update_state(self):
        if self.quantity <= 0:
            self.set_out_stock()
        elif self.quantity < self.safety_stock:
            self.set_low_stock()
        else:
            self.set_normal()
        self.save()

    @transition(field=state, source="*", target=SUPPLIER_STATE_OFTEN)
    def set_out_stock(self):
        pass

    @transition(field=state, source="*", target=SUPPLIER_STATE_HAPLY)
    def set_low_stock(self):
        pass

    @transition(field=state, source="*", target=SUPPLIER_STATE_NEVER)
    def set_normal(self):
        pass
