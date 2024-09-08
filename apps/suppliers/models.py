import re

from django.db import models
from django.utils import timezone


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

    def save(self, *args, **kwargs):
        self.telephone = self.format_telephone(self.telephone)
        super().save(*args, **kwargs)

    def format_telephone(self, number):
        # 把所有非數字符號改為空字串(清除)
        number = re.sub(r"\D", "", number)

        # 將輸入的電話號碼格式化為 09XX-XXXXXX 或 0X-XXXXXXX
        if len(number) == 10 and number.startswith("09"):
            return f"{number[:4]}-{number[4:]}"
        elif len(number) == 9 and number.startswith("0"):
            return f"{number[:2]}-{number[2:]}"
        else:
            return number
