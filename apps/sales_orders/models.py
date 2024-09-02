from django.db import models
from django_fsm import FSMField, transition

from apps.clients.models import Client
from apps.inventory.models import Inventory
from apps.products.models import Product


class SalesOrder(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    products = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    stock = models.ManyToManyField(Inventory)
    price = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    @property
    def stock_prices(self):
        return [item.price for item in self.stock.filter(product=self.products)]

    def __str__(self):
        return f"訂單 #{self.id} - 客戶: {self.client.name} ({self.created_at.date()})"

    STOCK_STATE_ABNORMAL = "unfinish"
    STOCK_STATE_NORMAL = "finish"

    STOCK_STATE_CHOICES = [
        (STOCK_STATE_ABNORMAL, "未完成"),
        (STOCK_STATE_NORMAL, "完成"),
    ]

    state = FSMField(
        default=STOCK_STATE_NORMAL,
        choices=STOCK_STATE_CHOICES,
        protected=True,
    )

    def update_state(self):
        if self.quantity < self.stock.safety_stock:
            self.set_stock_abnormal()
        else:
            self.set_normal()
        self.save()

    @transition(field=state, source="*", target=STOCK_STATE_ABNORMAL)
    def set_stock_abnormal(self):
        # 異常時的邏輯
        pass

    @transition(field=state, source="*", target=STOCK_STATE_NORMAL)
    def set_normal(self):
        # 正常時的邏輯
        pass

    def add_order(self, amount):

        self.update_state()

    def remove_order(self, amount):

        self.update_state()
