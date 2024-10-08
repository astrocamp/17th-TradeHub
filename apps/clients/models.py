import re

from django.db import models
from django.utils import timezone
from django_fsm import FSMField, transition

from apps.company.models import Company
from apps.users.models import CustomUser


class Client(models.Model):
    number = models.CharField(max_length=20)
    name = models.CharField(max_length=20)
    phone_number = models.CharField(max_length=15)
    address = models.CharField(max_length=150)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    company = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        related_name="clients",
        blank=True,
        null=True,
    )
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="clients",
        blank=True,
        null=True,
    )
    note = models.TextField(blank=True, null=True, max_length=150)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.phone_number = self.format_phone_number(self.phone_number)
        super().save(*args, **kwargs)
        self.number = f"C{self.id:03d}"
        super().save(update_fields=["number"])

    def format_phone_number(self, number):
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

    def format_phone_number(self, number):
        # 把所有非數字符號改為空字串(清除)
        number = re.sub(r"\D", "", number)

        # 將輸入的電話號碼格式化為 09XX-XXXXXX 或 0X-XXXXXXX
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
