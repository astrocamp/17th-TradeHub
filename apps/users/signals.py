from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.goods_receipts.models import GoodsReceipt
from apps.inventory.models import Inventory
from apps.orders.models import Order
from apps.purchase_orders.models import PurchaseOrder

from .models import Notification


@receiver(post_save, sender=Order)
def notify_order(sender, instance, created, **kwargs):
    if created:
        if instance.state == Order.TO_BE_CONFIRMED:
            notification = Notification(
                message=f"[訂單編號 {instance.order_number}]\n訂單已建立，庫存不足，請確認",
                sender_type="Order",
                sender_state="created",
            )
            notification.save()
        elif instance.state == Order.PROGRESS:
            notification = Notification(
                message=f"[訂單編號 {instance.order_number}]\n訂單已建立，且進入訂單流程",
                sender_type="Order",
                sender_state="progress",
            )
            notification.save()
    else:
        if instance.state == Order.PROGRESS:
            notification = Notification(
                message=f"[訂單編號 {instance.order_number}]\n訂單已進入訂單流程",
                sender_type="Order",
                sender_state="progress",
            )
            notification.save()
        elif instance.state == Order.FINISHED:
            notification = Notification(
                message=f"[訂單編號 {instance.order_number}]\n訂單已結案",
                sender_type="Order",
                sender_state="finished",
            )
            notification.save()


@receiver(post_save, sender=PurchaseOrder)
def notify_purchase_order(sender, instance, created, **kwargs):
    # previous_state = instance.__class__.objects.get(pk=instance.pk).state
    if created:
        if instance.state == PurchaseOrder.PENDING:
            notification = Notification(
                message=f"[採購單編號 {instance.order_number}]\n等待審核",
                sender_type="PurchaseOrder",
                sender_state="pending",
            )
            notification.save()
        elif instance.state == PurchaseOrder.PROGRESS:
            notification = Notification(
                message=f"[採購單編號 {instance.order_number}]\n已進入採購流程",
                sender_type="PurchaseOrder",
                sender_state="progress",
            )
            notification.save()
        elif instance.state == PurchaseOrder.FINISHED:
            notification = Notification(
                message=f"[採購單編號 {instance.order_number}]\n已結案",
                sender_type="PurchaseOrder",
                sender_state="finished",
            )
            notification.save()
    else:
        if instance.state == PurchaseOrder.PROGRESS:
            notification = Notification(
                message=f"[採購單編號 {instance.order_number}]\n已進入採購流程",
                sender_type="PurchaseOrder",
                sender_state="progress",
            )
            notification.save()
        elif instance.state == PurchaseOrder.FINISHED:
            notification = Notification(
                message=f"[採購單編號 {instance.order_number}]\n已結案",
                sender_type="PurchaseOrder",
                sender_state="finished",
            )
            notification.save()


@receiver(post_save, sender=GoodsReceipt)
def notify_goods_receipt(sender, instance, created, **kwargs):
    previous_state = instance.__class__.objects.get(pk=instance.pk).state
    if created:
        if instance.state == GoodsReceipt.TO_BE_RESTOCKED:
            notification = Notification(
                message=f"[進貨單編號 {instance.order_number}]\n待進貨",
                sender_type="GoodsReceipt",
                sender_state="to_be_restocked",
            )
            notification.save()
        elif instance.state == GoodsReceipt.TO_BE_STOCKED:
            notification = Notification(
                message=f"[進貨單編號{instance.order_number}]\n已進貨",
                sender_type="GoodsReceipt",
                sender_state="to_be_stocked",
            )
            notification.save()
        elif instance.state == GoodsReceipt.FINISHED:
            notification = Notification(
                message=f"[進貨單編號{instance.order_number}]\n已入庫",
                sender_type="GoodsReceipt",
                sender_state="finished",
            )
            notification.save()
    elif previous_state != instance.state:
        if instance.state == GoodsReceipt.TO_BE_STOCKED:
            notification = Notification(
                message=f"[進貨單編號{instance.order_number}]\n已進貨",
                sender_type="GoodsReceipt",
                sender_state="to_be_stocked",
            )
            notification.save()
        elif instance.state == GoodsReceipt.FINISHED:
            notification = Notification(
                message=f"[進貨單編號{instance.order_number}]\n已入庫",
                sender_type="GoodsReceipt",
                sender_state="finished",
            )
            notification.save()


# @receiver(post_save, sender=SalesOrder)
# def notify_sale_order(sender, instance, created, **kwargs):
#     previous_state = instance.__class__.objects.get(pk=instance.pk).state
#     if created and instance.state == SalesOrder.PENDING:
#         notification = Notification(
#             message=f"[銷貨單編號 {instance.order_number}] 等待審核",
#             sender_type="SaleOrder",
#             sender_state="pending",
#         )
#         notification.save()
#     elif instance.state == SalesOrder.PROGRESS:
#         if previous_state != SalesOrder.PROGRESS:
#             notification = Notification(
#                 message=f"[銷貨單編號{instance.order_number}] 已進入銷貨流程",
#                 sender_type="SalesOrder",
#                 sender_state="progress",
#             )
#             notification.save()
#     elif instance.state == SalesOrder.FINISHED:
#         if previous_state != SalesOrder.FINISHED:
#             notification = Notification(
#                 message=f"[銷貨單編號{instance.order_number}] 已結案",
#                 sender_type="SalesOrder",
#                 sender_state="finished",
#             )
#             notification.save()
