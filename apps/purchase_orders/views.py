import csv
import random
import string
from datetime import datetime, timedelta

import pandas as pd
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.forms import inlineformset_factory
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.timezone import timezone as tz
from django.views.decorators.http import require_POST

from apps.goods_receipts.models import GoodsReceipt, GoodsReceiptProductItem
from apps.products.models import Product
from apps.suppliers.models import Supplier

from .forms.purchase_orders_form import (
    ProductItemForm,
    ProductItemFormSet,
    PurchaseOrderForm,
)
from .models import ProductItem, PurchaseOrder


def index(request):
    state = request.GET.get("select")
    order_by = request.GET.get("sort", "id")
    is_desc = request.GET.get("desc", "True") == "False"

    purchase_orders = PurchaseOrder.objects.filter(user=request.user)

    if state in PurchaseOrder.AVAILABLE_STATES:
        purchase_orders = purchase_orders.filter(state=state, user=request.user)
    order_by_field = order_by if is_desc else "-" + order_by
    purchase_orders = purchase_orders.order_by(order_by_field)
    paginator = Paginator(purchase_orders, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    content = {
        "purchase_orders": page_obj,
        "selected_state": state,
        "order_by": order_by,
        "is_desc": is_desc,
        "page_obj": page_obj,
    }

    return render(request, "purchase_orders/index.html", content)


def new(request):
    if request.method == "POST":
        form = PurchaseOrderForm(request.POST, user=request.user)
        formset = ProductItemFormSet(
            request.POST, user=request.user, instance=form.instance
        )
        if form.is_valid() and formset.is_valid():
            order = form.save(commit=False)
            order.username = request.user.username
            order.user = request.user
            order.save()
            order.order_number = generate_order_number(order)
            order.save()
            formset.instance = order
            formset.save()
            messages.success(request, "新增完成!")
            return redirect("purchase_orders:index")
        else:
            return render(
                request, "purchase_orders/new.html", {"form": form, "formset": formset}
            )
    form = PurchaseOrderForm(user=request.user)
    formset = ProductItemFormSet(instance=form.instance, user=request.user)
    return render(
        request,
        "purchase_orders/new.html",
        {"form": form, "formset": formset},
    )


def show(request, id):
    purchase_order = get_object_or_404(PurchaseOrder, pk=id)
    product_items = ProductItem.objects.filter(purchase_order=purchase_order)
    return render(
        request,
        "purchase_orders/show.html",
        {"purchase_order": purchase_order, "product_items": product_items},
    )


def edit(request, id):
    purchase_order = get_object_or_404(PurchaseOrder, pk=id)
    if request.method == "POST":
        form = PurchaseOrderForm(request.POST, instance=purchase_order)
        formset = ProductItemFormSet(request.POST, instance=purchase_order)

        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, "更新完成!")
            return redirect("purchase_orders:show", purchase_order.id)
        return render(
            request,
            "purchase_orders/edit.html",
            {"purchase_order": purchase_order, "form": form, "formset": formset},
        )
    form = PurchaseOrderForm(instance=purchase_order)
    formset = get_product_item_formset(0)(instance=purchase_order)
    return render(
        request,
        "purchase_orders/edit.html",
        {"purchase_order": purchase_order, "form": form, "formset": formset},
    )


def delete(request, id):
    purchase_order = get_object_or_404(PurchaseOrder, pk=id)
    try:
        purchase_order.delete()
        messages.success(request, "刪除完成!")
        return redirect("purchase_orders:index")
    except:
        messages.success(request, "刪除完成!")
        return redirect("purchase_orders:index")


def get_product_item_formset(extra):
    return inlineformset_factory(
        PurchaseOrder,
        ProductItem,
        form=ProductItemForm,
        extra=extra,
        can_delete=True,
    )


def load_supplier_info(request):
    supplier_id = request.GET.get("supplier_id")
    supplier = Supplier.objects.get(id=supplier_id)
    products = Product.objects.filter(supplier=supplier).values(
        "id", "number", "product_name", "cost_price", "sale_price"
    )
    products_data = list(products)
    data = {
        "supplier_tel": supplier.telephone,
        "contact_person": supplier.contact_person,
        "supplier_email": supplier.email,
        "products": products_data,
    }
    return JsonResponse(data)


def load_product_info(request):
    product_id = request.GET.get("id")
    product = Product.objects.get(id=product_id)
    return JsonResponse({"cost_price": product.cost_price})


def generate_order_number(order):
    today = timezone.localtime().strftime("%Y%m%d")
    order_id = order.id
    order_suffix = f"{order_id:03d}"
    random_code_1 = "".join(random.choices(string.ascii_uppercase, k=2))
    random_code_2 = "".join(random.choices(string.ascii_uppercase, k=2))
    return f"{random_code_1}{today}{random_code_2}{order_suffix}"


def export_excel(request):
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = "attachment; filename=Purchase_Orders.xlsx"

    purchase_orders = (
        PurchaseOrder.objects.filter(user=request.user)
        .select_related("supplier")
        .prefetch_related("items__product")
        .values(
            "order_number",
            "supplier__name",
            "supplier_tel",
            "contact_person",
            "supplier_email",
            "created_at",
            "deleted_at",
            "items__product__product_name",
            "items__quantity",
            "items__cost_price",
            "items__subtotal",
            "amount",
            "note",
        )
    )

    df = pd.DataFrame(list(purchase_orders))

    for col in df.select_dtypes(include=["datetime64[ns, UTC]"]).columns:
        df[col] = df[col].dt.strftime("%Y-%m-%d %H:%M:%S")

    column_mapping = {
        "order_number": "序號",
        "supplier__name": "供應商名稱",
        "supplier_tel": "電話",
        "contact_person": "連絡人",
        "supplier_email": "Email",
        "created_at": "建立時間",
        "deleted_at": "刪除時間",
        "items__product__product_name": "商品",
        "items__quantity": "數量",
        "items__cost_price": "價格",
        "items__subtotal": "小計",
        "amount": "總金額",
        "note": "備註",
    }

    df.rename(columns=column_mapping, inplace=True)

    with pd.ExcelWriter(response, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Purchase_Orders")
    return response


@receiver(post_save, sender=PurchaseOrder)
def update_state(sender, instance, **kwargs):
    time_now = datetime.now(tz(timedelta(hours=+8))).strftime("%Y/%m/%d %H:%M:%S")
    if instance.state == PurchaseOrder.PENDING:
        if instance.is_finished:
            instance.set_progress()
            instance.is_finished = False
            instance.save()

    if instance.state == PurchaseOrder.PROGRESS:
        if instance.is_finished:
            items = ProductItem.objects.filter(purchase_order=instance)

            receipt = GoodsReceipt.objects.create(
                order_number=instance.order_number,
                user=instance.user,
                supplier=instance.supplier,
                supplier_tel=instance.supplier_tel,
                contact_person=instance.contact_person,
                supplier_email=instance.supplier_email,
                amount=0,
                note=f"訂單編號{instance.order_number}採購->進貨{time_now}",
            )

            for item in items:
                GoodsReceiptProductItem.objects.create(
                    goods_receipt=receipt,
                    product=item.product,
                    ordered_quantity=item.quantity,
                    received_quantity=0,
                    cost_price=item.cost_price,
                    subtotal=0,
                    user=instance.user,
                )
                # receipt.amount += receipt_item.subtotal

            receipt.save(update_fields=["amount"])
            instance.set_finished()
            instance.is_finished = False
            instance.save()


def transform_goods_receipt(request, id):
    purchase_order = get_object_or_404(PurchaseOrder, id=id)
    purchase_order.is_finished = True
    purchase_order.save()
    messages.success(request, "轉換成功!")
    return redirect("purchase_orders:index")
