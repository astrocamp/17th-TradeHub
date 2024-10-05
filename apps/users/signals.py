from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.goods_receipts.models import GoodsReceipt
from apps.inventory.models import Inventory
from apps.orders.models import Order
from apps.purchase_orders.models import PurchaseOrder
from apps.sales_orders.models import SalesOrder

from .models import CustomUser, Notification


@receiver(post_save, sender=Order)
def notify_order(sender, instance, **kwargs):
    if instance.order_number != "":
        if instance.state == Order.TO_BE_CONFIRMED:
            notification = Notification(
                message=f"[訂單編號{instance.order_number}]\n訂單已建立，且進入訂單流程",
                sender_type="Order",
                sender_state="to_be_confirmed",
                user=instance.user,
            )
            if not Notification.objects.filter(message=notification.message).exists():
                notification.save()

        elif instance.state == Order.PROGRESS:
            notification = Notification(
                message=f"[訂單編號{instance.order_number}]\n訂單已進入訂單流程",
                sender_type="Order",
                sender_state="progress",
                user=instance.user,
            )
            if not Notification.objects.filter(message=notification.message).exists():
                notification.save()
        elif instance.state == Order.FINISHED:
            notification = Notification(
                message=f"[訂單編號{instance.order_number}]\n訂單已結案",
                sender_type="Order",
                sender_state="finished",
                user=instance.user,
            )
            if not Notification.objects.filter(message=notification.message).exists():
                notification.save()


@receiver(post_save, sender=PurchaseOrder)
def notify_purchase_order(sender, instance, **kwargs):
    if instance.order_number != "":
        if instance.state == PurchaseOrder.PENDING:
            notification = Notification(
                message=f"[採購單編號{instance.order_number}]\n等待審核",
                sender_type="PurchaseOrder",
                sender_state="pending",
                user=instance.user,
            )
            if not Notification.objects.filter(message=notification.message).exists():
                notification.save()
        elif instance.state == PurchaseOrder.PROGRESS:
            notification = Notification(
                message=f"[採購單編號{instance.order_number}]\n已進入採購流程",
                sender_type="PurchaseOrder",
                sender_state="progress",
                user=instance.user,
            )
            if not Notification.objects.filter(message=notification.message).exists():
                notification.save()
        elif instance.state == PurchaseOrder.FINISHED:
            notification = Notification(
                message=f"[採購單編號{instance.order_number}]\n已結案",
                sender_type="PurchaseOrder",
                sender_state="finished",
                user=instance.user,
            )
            if not Notification.objects.filter(message=notification.message).exists():
                notification.save()


@receiver(post_save, sender=GoodsReceipt)
def notify_goods_receipt(sender, instance, **kwargs):
    if instance.order_number != "":
        if instance.state == GoodsReceipt.TO_BE_RESTOCKED:
            notification = Notification(
                message=f"[進貨單編號{instance.order_number}]\n待進貨",
                sender_type="GoodsReceipt",
                sender_state="to_be_restocked",
                user=instance.user,
            )
            if not Notification.objects.filter(message=notification.message).exists():
                notification.save()
        elif instance.state == GoodsReceipt.TO_BE_STOCKED:
            notification = Notification(
                message=f"[進貨單編號{instance.order_number}]\n已進貨",
                sender_type="GoodsReceipt",
                sender_state="to_be_stocked",
                user=instance.user,
            )
            if not Notification.objects.filter(message=notification.message).exists():
                notification.save()
        elif instance.state == GoodsReceipt.FINISHED:
            notification = Notification(
                message=f"[進貨單編號{instance.order_number}]\n已入庫",
                sender_type="GoodsReceipt",
                sender_state="finished",
                user=instance.user,
            )
            if not Notification.objects.filter(message=notification.message).exists():
                notification.save()


@receiver(post_save, sender=SalesOrder)
def notify_sale_order(sender, instance, **kwargs):
    if instance.order_number != "":
        if instance.state == SalesOrder.PENDING:
            notification = Notification(
                message=f"[銷貨單編號{instance.order_number}]\n待出貨",
                sender_type="SalesOrder",
                sender_state="pending",
                user=instance.user,
            )
            if not Notification.objects.filter(message=notification.message).exists():
                notification.save()
        elif instance.state == SalesOrder.FINISHED:
            notification = Notification(
                message=f"[銷貨單編號{instance.order_number}]\n已結案",
                sender_type="SalesOrder",
                sender_state="finished",
                user=instance.user,
            )
            if not Notification.objects.filter(message=notification.message).exists():
                notification.save()


@receiver(post_save, sender=Inventory)
def notify_inventory(sender, instance, **kwargs):
    if instance.number != "":
        if instance.state == Inventory.OUT_STOCK:
            notification = Notification(
                message=f"[庫存項目{instance.product.product_name}]\n已建立，目前庫存量為0",
                sender_type="Inventory",
                sender_state="out_stock",
                user=instance.user,
            )
            if not Notification.objects.filter(message=notification.message).exists():
                notification.save()
        elif instance.state == Inventory.LOW_STOCK:
            notification = Notification(
                message=f"[庫存項目{instance.product.product_name}]\n已建立，現有庫存低於預設安全庫存量",
                sender_type="Inventory",
                sender_state="low_stock",
                user=instance.user,
            )
            if not Notification.objects.filter(message=notification.message).exists():
                notification.save()


@receiver(post_save, sender=CustomUser)
def write_fake(sender, instance, created, **kwargs):
    import json

    from apps.clients.models import Client
    from apps.inventory.models import Inventory
    from apps.products.models import Product
    from apps.products.views import update_state
    from apps.suppliers.models import Supplier

    if created:
        with open("./fake_data/suppliers_data.json", "r", encoding="utf-8") as fake:
            template_data = json.load(fake)
        for items in template_data:
            data = items["fields"]
            Supplier.objects.create(
                number=data["number"],
                name=data["name"],
                address=data["address"],
                email=data["email"],
                gui_number=data["gui_number"],
                contact_person=data["contact_person"],
                telephone=data["telephone"],
                created_at=data["created_at"],
                updated_at=data["updated_at"],
                note=data["note"],
                user=instance,
            )

        with open("./fake_data/clients_data.json", "r", encoding="utf-8") as fake:
            template_data = json.load(fake)
        for items in template_data:
            data = items["fields"]
            Client.objects.create(
                number=data["number"],
                name=data["name"],
                phone_number=data["phone_number"],
                address=data["address"],
                email=data["email"],
                created_at=data["created_at"],
                updated_at=data["updated_at"],
                note=data["note"],
                user=instance,
            )

        post_save.disconnect(update_state, sender=Product)
        with open("./fake_data/products_data.json", "r", encoding="utf-8") as fake:
            template_data = json.load(fake)
        for items in template_data:
            data = items["fields"]
            Product.objects.create(
                number=data["number"],
                supplier=Supplier.objects.get(pk=data["supplier"]),
                note=data["note"],
                sale_price=data["sale_price"],
                cost_price=data["cost_price"],
                created_at=data["created_at"],
                updated_at=data["updated_at"],
                product_name=data["product_name"],
                user=instance,
            )
        post_save.connect(update_state, sender=Product)

        with open("./fake_data/inventory_data.json", "r", encoding="utf-8") as fake:
            template_data = json.load(fake)
        for items in template_data:
            data = items["fields"]
            Inventory.objects.create(
                number=data["number"],
                product=Product.objects.get(pk=data["product"]),
                supplier=Supplier.objects.get(pk=data["supplier"]),
                quantity=data["quantity"],
                safety_stock=data["safety_stock"],
                created_at=data["created_at"],
                deleted_at=data.get("deleted_at"),
                note=data["note"],
                last_updated=data["last_updated"],
                user=instance,
            )
