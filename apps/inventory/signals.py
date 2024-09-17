from django.db.models.signals import pre_save
from django.dispatch import receiver

from apps.goods_receipts.models import GoodsReceipt

from .models import Inventory


@receiver(pre_save, sender=Inventory)
def update_state(sender, instance, **kwargs):
    if instance.quantity <= 0:
        instance.set_out_stock()
    elif instance.quantity < instance.safety_stock:
        instance.set_low_stock()
    else:
        instance.set_normal()


@receiver(pre_save, sender=GoodsReceipt)
def update_inventory(sender, instance, **kwargs):
    if instance.state == "FINISHED":
        if Inventory.product in instance.goods_name:
            inventory = Inventory.objects.get(product=instance.product)
            inventory.quantity += instance.quantity
        inventory.save()
