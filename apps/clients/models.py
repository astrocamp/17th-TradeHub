import re

from django.db import models
from django_fsm import FSMField, transition


class Client(models.Model):
    name = models.CharField(max_length=20)
    phone_number = models.CharField(max_length=15)
    address = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    delete_at = models.DateTimeField(auto_now=True)
    note = models.TextField(blank=True, null=True, max_length=150)

    def __str__(self):
        return self.name

    CLIENT_STATE_OFTEN = "often"
    CLIENT_STATE_HAPLY = "haply"
    CLIENT_STATE_NEVER = "never"

    CLIENT_STATE_CHOICES = [
        (CLIENT_STATE_OFTEN, "經常"),
        (CLIENT_STATE_HAPLY, "偶爾"),
        (CLIENT_STATE_NEVER, "從不"),
    ]

    state = FSMField(
        default=CLIENT_STATE_NEVER,
        choices=CLIENT_STATE_CHOICES,
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

    @transition(field=state, source="*", target=CLIENT_STATE_OFTEN)
    def set_out_stock(self):
        pass

    @transition(field=state, source="*", target=CLIENT_STATE_HAPLY)
    def set_low_stock(self):
        pass

    @transition(field=state, source="*", target=CLIENT_STATE_NEVER)
    def set_normal(self):
        pass

    def save(self, *args, **kwargs):
        self.phone_number = self.format_phone_number(self.phone_number)
        super().save(*args, **kwargs)

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
