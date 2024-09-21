import csv

import pandas as pd
import pytz
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.forms import inlineformset_factory
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.goods_receipts.models import GoodsReceipt
from apps.inventory.models import Inventory
from apps.products.models import Product
from apps.suppliers.models import Supplier

from .forms.goods_receipts_form import (
    FileUploadForm,
    GoodsReceiptForm,
    GoodsReceiptProductItemForm,
    ProductItemFormSet,
)
from .models import GoodsReceipt, GoodsReceiptProductItem

# from datetime import datetime, timedelta, timezone


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
    new_order_number = generate_order_number()
    if request.method == "POST":
        form = GoodsReceiptForm(request.POST)
        formset = ProductItemFormSet(request.POST, instance=form.instance)
        if form.is_valid() and formset.is_valid():
            order = form.save(commit=False)
            order.order_number = new_order_number
            order.username = request.user.username
            order.save()
            formset.instance = order
            formset.save()
            return redirect("goods_receipts:index")
        else:
            return render(
                request, "goods_receipts/new.html", {"form": form, "formset": formset}
            )
    form = GoodsReceiptForm()
    form = GoodsReceiptForm(initial={"order_number": new_order_number})
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
    goods_receipt = get_object_or_404(GoodsReceipt, pk=id)
    goods_receipt.delete()
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
        "id", "product_number", "product_name", "cost_price", "sale_price"
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


def generate_order_number():
    today = timezone.localtime().strftime("%Y%m%d")
    last_order = (
        GoodsReceipt.all_objects.filter(order_number__startswith=today)
        .order_by("-order_number")
        .first()
    )

    if last_order:
        last_order_number = int(last_order.order_number[-3:])
        new_order_number = f"{last_order_number + 1:03d}"
    else:
        new_order_number = "001"

    return f"{today}{new_order_number}"


def import_file(request):
    if request.method == "POST":
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES["file"]
            if file.name.endswith(".csv"):

                decoded_file = file.read().decode("utf-8").splitlines()
                reader = csv.reader(decoded_file)
                next(reader)

                for row in reader:
                    if len(row) < 1:
                        continue
                    try:
                        supplier = Supplier.objects.get(id=row[1])
                        goods_name = Product.objects.get(id=row[2])
                        GoodsReceipt.objects.create(
                            receipt_number=row[0],
                            supplier=supplier,
                            goods_name=goods_name,
                            quantity=row[3],
                            method=row[4],
                            note=row[5],
                        )
                    except (Supplier.DoesNotExist, Product.DoesNotExist) as e:
                        messages.error(request, f"匯入失敗，找不到廠商或商品: {e}")
                        return redirect("goods_receipts:index")

                messages.success(request, "成功匯入 CSV")
                return redirect("goods_receipts:index")

            elif file.name.endswith(".xlsx"):
                df = pd.read_excel(file)
                df.rename(
                    columns={
                        "收據號碼": "receipt_number",
                        "供應商": "supplier",
                        "商品": "goods_name",
                        "數量": "quantity",
                        "傳送方式": "method",
                        "備註": "note",
                    },
                    inplace=True,
                )
                for _, row in df.iterrows():
                    try:
                        goods_name = Product.objects.get(id=int(row["goods_name"]))
                        supplier = Supplier.objects.get(id=int(row["supplier"]))
                        GoodsReceipt.objects.create(
                            receipt_number=str(row["receipt_number"]),
                            supplier=supplier,
                            goods_name=goods_name,
                            quantity=str(row["quantity"]),
                            method=str(row[4]),
                            note=str(row["note"]) if not pd.isna(row["note"]) else "",
                        )
                    except (Supplier.DoesNotExist, Product.DoesNotExist) as e:
                        messages.error(request, f"匯入失敗，找不到廠商或商品: {e}")
                        return redirect("goods_receipts:index")
                messages.success(request, "成功匯入 Excel")
                return redirect("goods_receipts:index")

            else:
                messages.error(request, "匯入失敗(檔案不是 CSV 或 Excel)")
                return render(request, "layouts/import.html", {"form": form})

    form = FileUploadForm()
    return render(request, "layouts/import.html", {"form": form})


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

    # @receiver(pre_save, sender=GoodsReceipt)
    # def update_state(sender, instance, **kwargs):
    utc_8 = pytz.timezone("Asia/Taipei")
    time_now = timezone.now().astimezone(utc_8).strftime("%Y/%m/%d %H:%M:%S")
    if instance.purchase_quantity < instance.order_quantity:
        if instance.is_finished:
            instance.order_quantity -= instance.purchase_quantity
            instance.note += f"{time_now} 入庫{instance.purchase_quantity}個：{instance.goods_name}，剩餘{instance.order_quantity}個"
            if Inventory.objects.filter(
                product=instance.goods_name, supplier=instance.supplier
            ).exists():
                inventory = Inventory.objects.get(
                    product=instance.goods_name, supplier=instance.supplier
                )
                inventory.quantity += instance.purchase_quantity
                inventory.last_updated = time_now
                inventory.note += f"{time_now} 入庫{instance.purchase_quantity}個：{instance.goods_name}"
                inventory.save()
            else:
                Inventory.objects.create(
                    product=instance.goods_name,
                    supplier=instance.supplier,
                    quantity=instance.purchase_quantity,
                    safety_stock=0,
                    note=f"{time_now} 新進貨物{instance.goods_name}：{instance.purchase_quantity}個，供應商：{instance.supplier}，收據號碼：{instance.receipt_number}",
                    last_updated=time_now,
                )
            instance.purchase_quantity = 0
            instance.is_finished = False
    instance.set_to_be_restocked()
    if instance.purchase_quantity >= instance.order_quantity:
        instance.set_to_be_stocked()
        if instance.is_finished:
            if Inventory.objects.filter(
                product=instance.goods_name, supplier=instance.supplier
            ).exists():
                inventory = Inventory.objects.get(
                    product=instance.goods_name, supplier=instance.supplier
                )
                inventory.quantity += instance.purchase_quantity
                inventory.last_updated = time_now
                inventory.note += f"{time_now} 入庫{instance.purchase_quantity}個：{instance.goods_name}"
                inventory.save()
            else:
                Inventory.objects.create(
                    product=instance.goods_name,
                    supplier=instance.supplier,
                    quantity=instance.purchase_quantity,
                    safety_stock=0,
                    note=f"{time_now} 新進貨物{instance.goods_name}：{instance.purchase_quantity}個，供應商：{instance.supplier}，收據號碼：{instance.receipt_number}",
                    last_updated=time_now,
                )
            instance.note += (
                f"{time_now} 入庫{instance.purchase_quantity}個：{instance.goods_name}"
            )
            instance.order_quantity -= instance.purchase_quantity
            instance.purchase_quantity = 0
            instance.set_finished()


def stocked(request, id):
    goods_receipt = get_object_or_404(GoodsReceipt, id=id)
    goods_receipt.is_finished = True
    goods_receipt.save()
    messages.success(request, "入庫完成!")
    return redirect("goods_receipts:index")
