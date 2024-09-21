from django.db import models
from django_fsm import FSMField, transition

from apps.products.models import Product
from apps.purchase_orders.models import ProductItem, PurchaseOrder
from apps.purchase_orders.views import generate_order_number
from apps.suppliers.models import Supplier


class Inventory(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name="inventories"
    )
    supplier = models.ForeignKey(
        Supplier, on_delete=models.PROTECT, related_name="inventories"
    )
    quantity = models.PositiveIntegerField()
    safety_stock = models.PositiveIntegerField()
    last_updated = models.DateTimeField(auto_now=True)
    note = models.TextField(blank=True)

    def __str__(self):
        return f"{self.product} - {self.get_state_display()} ({self.quantity})"

    OUT_STOCK = "out_stock"
    LOW_STOCK = "low_stock"
    NORMAL = "normal"
    NEW_STOCK = "new_stock"

    AVAILABLE_STATES = OUT_STOCK, LOW_STOCK, NORMAL

    STATES_CHOICES = [
        (OUT_STOCK, "缺貨"),
        (LOW_STOCK, "低於安全庫存量"),
        (NORMAL, "正常"),
        (NEW_STOCK, "新庫存"),
    ]

    state = FSMField(
        default=NORMAL,
        choices=STATES_CHOICES,
        protected=True,
    )

    @transition(field=state, source="*", target=OUT_STOCK)
    def set_out_stock(self):
        if not PurchaseOrder.objects.filter(
            supplier=self.supplier, state=PurchaseOrder.PROGRESS
        ):
            message = f"庫存於缺貨狀態，自動下單 {self.safety_stock} 個 {self.product}"
            supplier = Supplier.objects.get(name=self.supplier.name)
            purchase_order = PurchaseOrder.objects.create(
                order_number=generate_order_number(),
                supplier=self.supplier,
                supplier_tel=supplier.telephone,
                contact_person=supplier.contact_person,
                supplier_email=supplier.email,
                amount=0,
                note=message,
                state=PurchaseOrder.PROGRESS,
            )
            ProductItem.objects.create(
                purchase_order=purchase_order,
                product=self.product,
                quantity=self.safety_stock,
                cost_price=0,
                subtotal=0,
            )

    @transition(field=state, source="*", target=LOW_STOCK)
    def set_low_stock(self):
        if not PurchaseOrder.objects.filter(
            supplier=self.supplier, state=PurchaseOrder.PENDING
        ):
            message = f"庫存低於安全庫存量，自動下單 {self.safety_stock - self.quantity} 個 {self.product}"
            supplier = Supplier.objects.get(name=self.supplier.name)
            purchase_order = PurchaseOrder.objects.create(
                order_number=generate_order_number(),
                supplier=self.supplier,
                supplier_tel=supplier.telephone,
                contact_person=supplier.contact_person,
                supplier_email=supplier.email,
                amount=0,
                note=message,
                state=PurchaseOrder.PENDING,
            )
            ProductItem.objects.create(
                purchase_order=purchase_order,
                product=self.product,
                quantity=self.safety_stock - self.quantity,
                cost_price=0,
                subtotal=0,
            )

    @transition(field=state, source="*", target=NORMAL)
    def set_normal(self):
        pass

    @transition(field=state, source="*", target=NEW_STOCK)
    def set_new_stock(self):
        pass
