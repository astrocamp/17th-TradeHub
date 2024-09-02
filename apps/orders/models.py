from django.db import models

from ..clients.models import Client
from ..products.models import Product


class Orders(models.Model):
    code = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(auto_now=True)
    product_fk = models.ForeignKey(Product, on_delete=models.PROTECT)
    client_fk = models.ForeignKey(Client, on_delete=models.PROTECT)
    note = models.TextField(blank=True)
