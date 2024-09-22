from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from apps.goods_receipts.models import GoodsReceipt
from apps.purchase_orders.models import PurchaseOrder


class CustomUser(AbstractUser):

    DEPARTMENT_CHOICES = [
        ("", "Select Department"),
        ("Purchasing", "Purchasing"),
        ("Inventory", "Inventory"),
        ("HR", "Human Resources"),
    ]

    POSITION_CHOICES = [
        ("", "Select Position"),
        ("Intern", "Intern"),
        ("Specialist", "Specialist"),
        ("Manager", "Manager"),
        ("BOSS", "BOSS"),
    ]

    email = models.EmailField(unique=True)
    birthday = models.DateField(blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.CharField(max_length=100, blank=False, null=False, default="")
    department = models.CharField(
        choices=DEPARTMENT_CHOICES, max_length=20, default="", blank=False, null=False
    )
    position = models.CharField(
        choices=POSITION_CHOICES, max_length=20, default="", blank=False, null=False
    )
    hire_date = models.DateTimeField(default=timezone.now)
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.username}"

    class Meta:

        permissions = [
            # 設置權限類別
            ("can_edit_department", "Can edit department"),
            ("can_edit_position", "Can edit position"),
            ("can_edit_hire_date", "Can edit hire date"),
        ]


class Notification(models.Model):
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.message}-{self.created_at}"


# 採購單-通知待審核ok,elif邏輯還沒
@receiver(post_save, sender=PurchaseOrder)
def notify_purchase_order(sender, instance, created, **kwargs):
    if created and instance.state == PurchaseOrder.PENDING:
        notification = Notification(
            message=f"[採購單編號 {instance.order_number}] 等待審核",
        )
        notification.save()
    # elif not created:
    #     previous_state = PurchaseOrder.objects.get(pk=instance.pk).state
    #     if previous_state != instance.state:
    #         notification = Notification(
    #             message=f"[採購單編號({instance.order_number})] 狀態變更，等待審核",
    #         )
    #         notification.save()


# @receiver(post_save, sender=GoodsReceipt)
# def notify_goods_receipt(sender, instance, created, **kwargs):
#     if created and instance.state == GoodsReceipt.TO_BE_RESTOCKED:
#         notification = Notification(
#             message=f"[進貨單編號 {instance.receipt_number}] 等待審核",
#         )
#         notification.save()
