from django.db import models
from django.utils import timezone

from ..clients.models import Client
from ..products.models import Product


class Orders(models.Model):
    code = models.CharField(max_length=15)
    client_fk = models.ForeignKey(Client, on_delete=models.PROTECT)
    product_fk = models.ForeignKey(Product, on_delete=models.PROTECT)
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def soft_delete(self):
        self.deleted_at = timezone.now()
        self.save()
