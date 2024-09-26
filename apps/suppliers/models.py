import re

from django.db import models
from django.utils import timezone
from django_fsm import FSMField, transition

from apps.company.models import Company
from apps.users.models import CustomUser


class SupplierManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at=None)


class Supplier(models.Model):
    number = models.CharField(max_length=20)
    name = models.CharField(max_length=20)
    telephone = models.CharField(max_length=15)
    contact_person = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    gui_number = models.CharField(max_length=8, unique=True)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    company = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        related_name="suppliers",
        blank=True,
        null=True,
    )
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, blank=True, null=True
    )
    note = models.TextField(blank=True, null=True)

    objects = SupplierManager()

    def delete(self):
        self.deleted_at = timezone.now()
        self.save()

    def __str__(self):
        return f"{self.name} ({self.gui_number})"

    # def save(self, *args, **kwargs):
    #     self.phone_number = self.format_telephone_number(self.telephone)
    #     super().save(*args, **kwargs)
    #     self.number = f"S{self.id:03d}"
    #     super().save(update_fields=["number"])

    def format_telephone_number(self, number):
        number = re.sub(r"\D", "", number)
        if len(number) == 10 and number.startswith("09"):
            return f"{number[:4]}-{number[4:]}"
        elif len(number) == 10 and number.startswith(("037", "049")):
            return f"{number[:3]}-{number[3:]}"
        elif len(number) == 10:
            return f"{number[:2]}-{number[2:]}"
        elif len(number) == 9 and number.startswith("0"):
            return f"{number[:2]}-{number[2:]}"
        else:
            return number

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

    @transition(field=state, source="*", target=OFTEN)
    def set_often(self):
        pass

    @transition(field=state, source="*", target=HAPLY)
    def set_haply(self):
        pass

    @transition(field=state, source="*", target=NEVER)
    def set_never(self):
        pass
