import re

from django.db import models
from django_fsm import FSMField, transition


class Supplier(models.Model):
    name = models.CharField(max_length=20)
    telephone = models.CharField(max_length=15)
    contact_person = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    gui_number = models.CharField(max_length=8, unique=True)
    address = models.TextField()
    established_date = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True, null=True)

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

    def save(self, *args, **kwargs):
        self.telephone = self.format_telephone(self.telephone)
        super().save(*args, **kwargs)

    def format_telephone(self, number):
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
