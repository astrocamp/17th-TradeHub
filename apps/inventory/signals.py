from django.dispatch import receiver
from django.db.models.signals import pre_save

from .models import Inventory


@receiver(pre_save, sender=Inventory)
def update_state(sender, instance, **kwargs):
    if instance.quantity <= 0:
        instance.set_out_stock()
    elif instance.quantity < instance.safety_stock:

        instance.set_low_stock()
    else:
        instance.set_normal()
