import csv
import random
import string
from datetime import datetime, timedelta
from datetime import timezone as tz

import pandas as pd
import pytz
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.forms import inlineformset_factory
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.goods_receipts.models import GoodsReceipt, Product, Supplier
from apps.inventory.models import Inventory

from .forms.goods_receipts_form import (
    GoodsReceiptForm,
    GoodsReceiptProductItemForm,
    ProductItemFormSet,
)
from .models import GoodsReceipt, GoodsReceiptProductItem


def index(request):
    state = request.GET.get("select")
    order_by = request.GET.get("sort", "id")
    is_desc = request.GET.get("desc", "True") == "False"

    goods_receipts = GoodsReceipt.objects.all()

    if state in GoodsReceipt.AVAILABLE_STATES:
        goods_receipts = GoodsReceipt.objects.filter(state=state)
    order_by_field = order_by if is_desc else "-" + order_by
    goods_receipts = goods_receipts.order_by(order_by_field)
    paginator = Paginator(goods_receipts, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    content = {
        "goods_receipts": page_obj,
        "selected_state": state,
        "is_desc": is_desc,
        "order_by": order_by,
        "page_obj": page_obj,
    }

    return render(request, "goods_receipts/index.html", content)


def new(request):
    if request.method == "POST":
        form = GoodsReceiptForm(request.POST)
        formset = ProductItemFormSet(request.POST, instance=form.instance)
        if form.is_valid() and formset.is_valid():
            order = form.save(commit=False)
            order.username = request.user.username
            order.user = request.user
            with transaction.atomic():
                order.order_number = generate_order_number(GoodsReceipt)
                formset.instance = order
                order.save()
            return redirect("goods_receipts:index")
        else:
            return render(
                request, "goods_receipts/new.html", {"form": form, "formset": formset}
            )
    form = GoodsReceiptForm()
    formset = ProductItemFormSet(instance=form.instance)
    return render(
        request,
        "goods_receipts/new.html",
        {"form": form, "formset": formset},
    )


def show(request, id):
    goods_receipt = get_object_or_404(GoodsReceipt, pk=id)
    product_items = GoodsReceiptProductItem.objects.filter(goods_receipt=goods_receipt)
    return render(
        request,
        "goods_receipts/show.html",
        {"goods_receipt": goods_receipt, "product_items": product_items},
    )


def edit(request, id):
    goods_receipt = get_object_or_404(GoodsReceipt, pk=id)
    if request.method == "POST":
        form = GoodsReceiptForm(request.POST, instance=goods_receipt)
        formset = ProductItemFormSet(request.POST, instance=goods_receipt)
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                form.save()
                formset.save()
            return redirect("goods_receipts:show", goods_receipt.id)
        return render(
            request,
            "goods_receipts/edit.html",
            {"goods_receipt": goods_receipt, "form": form, "formset": formset},
        )
    form = GoodsReceiptForm(instance=goods_receipt)
    formset = get_product_item_formset(0)(instance=goods_receipt)
    return render(
        request,
        "goods_receipts/edit.html",
        {"goods_receipt": goods_receipt, "form": form, "formset": formset},
    )


def delete(request, id):
    purchase_order = get_object_or_404(GoodsReceipt, pk=id)
    try:
        purchase_order.delete()
        messages.success(request, "刪除完成!")
        return redirect("goods_receipts:index")
    except:
        messages.success(request, "刪除完成!")
        return redirect("goods_receipts:index")


@require_POST
def delete_selected_goods_receipts(request):
    selected_goods_receipts = request.POST.getlist("selected_goods_receipts")
    GoodsReceipt.objects.filter(id__in=selected_goods_receipts).delete()
    return redirect("goods_receipts:index")


def get_product_item_formset(extra):
    return inlineformset_factory(
        GoodsReceipt,
        GoodsReceiptProductItem,
        form=GoodsReceiptProductItemForm,
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


# def generate_order_number(order):
#     today = timezone.localtime().strftime("%Y%m%d")
#     order_id = order.id
#     order_suffix = f"{order_id:03d}"
#     random_code_1 = "".join(random.choices(string.ascii_uppercase, k=2))
#     random_code_2 = "".join(random.choices(string.ascii_uppercase, k=2))
#     return f"{random_code_1}{today}{random_code_2}{order_suffix}"


def generate_order_number(model_name):
    today = timezone.localtime().strftime("%Y%m%d")
    today_num = bool(model_name.objects.filter(name__contains=today).last())
    order_suffix = f"{today_num:03d}"
    random_code_1 = "".join(random.choices(string.ascii_uppercase, k=2))
    if today_num:
        return f"{today}{random_code_1}{order_suffix+1}"
    else:
        return f"{today}{random_code_1}001"


def export_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="GoodsReceipts.csv"'

    writer = csv.writer(response)
    writer.writerow(
        [
            "收據號碼",
            "供應商",
            "商品",
            "數量",
            "傳送方式",
            "建立時間",
            "刪除時間",
            "備註",
        ]
    )

    goods_receipts = GoodsReceipt.objects.all()
    for goods_receipt in goods_receipts:
        writer.writerow(
            [
                goods_receipt.receipt_number,
                goods_receipt.supplier,
                goods_receipt.goods_name,
                goods_receipt.quantity,
                goods_receipt.method,
                goods_receipt.date,
                goods_receipt.deleted_at,
                goods_receipt.note,
            ]
        )

    return response


def export_excel(request):
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = "attachment; filename=GoodsReceipts.xlsx"

    goods_receipts = GoodsReceipt.objects.select_related("product", "supplier").values(
        "receipt_number",
        "supplier__name",
        "goods_name__product_name",
        "quantity",
        "method",
        "date",
        "deleted_at",
        "note",
    )

    df = pd.DataFrame(goods_receipts)
    for col in df.select_dtypes(include=["datetime64[ns, UTC]"]).columns:
        df[col] = df[col].dt.strftime("%Y-%m-%d")

    column_mapping = {
        "receipt_number": "收據號碼",
        "supplier__name": "供應商",
        "goods_name__product_name": "商品",
        "quantity": "數量",
        "method": "傳送方式",
        "date": "建立時間",
        "deleted_at": "刪除時間",
        "note": "備註",
    }

    df.rename(columns=column_mapping, inplace=True)

    with pd.ExcelWriter(response, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="GoodsReceipts")
    return response


@receiver(post_save, sender=GoodsReceipt)
def update_state(sender, instance, **kwargs):
    time_now = datetime.now(tz(timedelta(hours=+8))).strftime("%Y/%m/%d %H:%M:%S")
    receipts_items = GoodsReceiptProductItem.objects.filter(goods_receipt=instance)

    post_save.disconnect(update_state, sender=GoodsReceipt)
    for item in receipts_items:
        if item.received_quantity < item.ordered_quantity:
            instance.set_to_be_restocked()
            instance.save()
            if instance.is_finished and item.received_quantity != 0:
                instance.note += f"入庫{item.received_quantity}個：{item.product}，剩餘{item.ordered_quantity}個{time_now}\n"
                inventory = Inventory.objects.filter(product=item.product).first()

                if inventory:

                    with transaction.atomic():
                        quantity = inventory.quantity + item.received_quantity
                        note = (
                            inventory.note
                            + f"入庫{item.received_quantity}個：{item.product}{time_now}"
                        )
                        Inventory.objects.filter(product=item.product).update(
                            quantity=quantity,
                            last_updated=timezone.now(),
                            note=note,
                        )
                # else:
                #     Inventory.objects.create(
                #         product=item.product,
                #         supplier=instance.supplier,
                #         quantity=item.received_quantity,
                #         safety_stock=0,
                #         note=f"新進貨物{item.product}：{item.received_quantity}個，供應商：{instance.supplier}，收據號碼：{instance.supplier}，收據號碼：{instance.order_number}{time_now}",
                #         last_updated=time_now,
                #     )

                item.ordered_quantity -= item.received_quantity
                item.received_quantity = 0
                item.save(update_fields=["received_quantity", "ordered_quantity"])

        if item.received_quantity == item.ordered_quantity:
            if instance.is_finished and item.received_quantity != 0:
                inventory = Inventory.objects.filter(product=item.product).first()
                if inventory:

                    with transaction.atomic():
                        inventory.quantity += item.received_quantity
                        inventory.last_updated = time_now
                        inventory.note += f"入庫{item.received_quantity}個：{item.product}{time_now}\n"
                        inventory.save(
                            update_fields=["quantity", "last_updated", "note"]
                        )
                # else:
                #     Inventory.objects.create(
                #         product=item.product,
                #         supplier=instance.supplier,
                #         quantity=item.received_quantity,
                #         safety_stock=0,
                #         note=f"新進貨物{item.product}：{item.received_quantity}個，供應商：{instance.supplier}，收據號碼：{instance.receipt_number}{time_now}",
                #         last_updated=time_now,
                #     )

                instance.note += (
                    f"入庫{item.received_quantity}個：{item.product}{time_now}"
                )
                item.ordered_quantity = 0
                item.received_quantity = 0
                item.save(update_fields=["received_quantity", "ordered_quantity"])
    instance.is_finished = False

    ordered_quantity = [item.ordered_quantity for item in receipts_items]
    received_quantity = [item.received_quantity for item in receipts_items]

    if ordered_quantity != received_quantity:
        instance.set_to_be_stocked()
        instance.save()
        if 0 in received_quantity:
            instance.set_to_be_restocked()
            instance.save()
    if sum(ordered_quantity) == 0:
        instance.set_finished()
        instance.save()
    post_save.connect(update_state, sender=GoodsReceipt)


def stocked(request, id):
    goods_receipt = get_object_or_404(GoodsReceipt, id=id)
    goods_receipt.is_finished = True
    post_save.send(sender=GoodsReceipt, instance=goods_receipt, created=True)
    messages.success(request, "入庫完成!")
    return redirect("goods_receipts:index")
