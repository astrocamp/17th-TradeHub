import csv

import pandas as pd
from django.contrib import messages
from django.core.paginator import Paginator
from django.forms import inlineformset_factory
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.products.models import Product
from apps.suppliers.models import Supplier

from .forms.purchase_orders_form import (
    FileUploadForm,
    ProductItemForm,
    ProductItemFormSet,
    PurchaseOrderForm,
)
from .models import ProductItem, PurchaseOrder


def index(request):
    state = request.GET.get("select")
    order_by = request.GET.get("sort", "id")
    is_desc = request.GET.get("desc", "True") == "False"

    purchase_orders = PurchaseOrder.objects.all()

    if state in PurchaseOrder.AVAILABLE_STATES:
        purchase_orders = purchase_orders.filter(state=state)
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

    if request.method == "POST":
        form = PurchaseOrderForm(request.POST)
        formset = ProductItemFormSet(request.POST, instance=form.instance)
        if form.is_valid() and formset.is_valid():
            order = form.save()
            formset.instance = order
            formset.save()
            return redirect("purchase_orders:index")
        else:
            return render(
                request, "purchase_orders/new.html", {"form": form, "formset": formset}
            )

    purchase_orders = PurchaseOrder.objects.order_by("id")
    return render(
        request, "purchase_orders/index.html", {"purchase_orders": purchase_orders}
    )


from django.utils import timezone

from .models import PurchaseOrder


def new(request):
    today = timezone.localtime().strftime("%Y%m%d")
    last_order = (
        PurchaseOrder.objects.filter(order_number__startswith=today)
        .order_by("-order_number")
        .first()
    )
    if last_order:
        last_order_number = int(last_order.order_number[-3:])
        new_order_number = f"{today}{last_order_number + 1:03d}"
    else:
        new_order_number = f"{today}001"

    form = PurchaseOrderForm(initial={"order_number": new_order_number})
    formset = ProductItemFormSet(instance=form.instance)
    return render(
        request,
        "purchase_orders/new.html",
        {"form": form, "formset": formset},
    )


def show(request, id):
    purchase_order = get_object_or_404(PurchaseOrder, id=id)
    if request.method == "POST":
        form = PurchaseOrderForm(request.POST, instance=purchase_order)
        formset = ProductItemFormSet(request.POST, instance=purchase_order)

        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect("purchase_orders:show", purchase_order.id)

        else:
            return render(
                request,
                "purchase_orders/edit.html",
                {"form": form, "formset": formset, "purchase_order": purchase_order},
            )

    product_items = ProductItem.objects.filter(purchase_order=purchase_order)
    return render(
        request,
        "purchase_orders/show.html",
        {"purchase_order": purchase_order, "product_items": product_items},
    )


def edit(request, id):
    purchase_order = get_object_or_404(PurchaseOrder, id=id)
    form = PurchaseOrderForm(instance=purchase_order)
    formset = get_product_item_formset(0)(instance=purchase_order)
    return render(
        request,
        "purchase_orders/edit.html",
        {"form": form, "formset": formset, "purchase_order": purchase_order},
    )


def get_product_item_formset(extra):
    return inlineformset_factory(
        PurchaseOrder,
        ProductItem,
        form=ProductItemForm,
        extra=extra,
        can_delete=True,
    )


def delete(request, id):
    purchase_order = get_object_or_404(PurchaseOrder, pk=id)
    purchase_order.delete()
    return redirect("purchase_orders:index")


@require_POST
def delete_selected_purchase_orders(request):
    selected_purchase_orders = request.POST.getlist("selected_purchase_orders")
    PurchaseOrder.objects.filter(id__in=selected_purchase_orders).delete()
    return redirect("purchase_orders:index")


def load_supplier_info(request):
    supplier_id = request.GET.get("supplier_id")
    supplier = Supplier.objects.get(id=supplier_id)
    data = {
        "supplier_tel": supplier.telephone,
        "contact_person": supplier.contact_person,
        "supplier_email": supplier.email,
    }
    return JsonResponse(data)


def import_file(request):
    form = FileUploadForm(request.POST, request.FILES)
    if form.is_valid():
        file = request.FILES["file"]
        if file.name.endswith(".csv"):

            decoded_file = file.read().decode("utf-8").splitlines()
            reader = csv.reader(decoded_file)
            next(reader)  # Skip header row

            for row in reader:
                if len(row) < 11:
                    # messages.error(request, f"CSV 数据不完整，跳过该行: {row}")
                    continue

                try:
                    supplier = Supplier.objects.get(id=row[1])

                    purchase_order, created = PurchaseOrder.objects.get_or_create(
                        order_number=row[0],
                        supplier=supplier,
                        supplier_tel=row[2],
                        contact_person=row[3],
                        supplier_email=row[4],
                        total_amount=row[9],
                        notes=row[10],
                    )

                    product = Product.objects.get(id=row[5])
                    ProductItem.objects.create(
                        purchase_order=purchase_order,
                        product=product,
                        quantity=row[6],
                        price=row[7],
                        subtotal=row[8],
                    )

                except Supplier.DoesNotExist as e:
                    messages.error(request, f"匯入失敗，找不到供應商: {e}")
                    return redirect("purchase_orders:import_file")
                except Product.DoesNotExist as e:
                    messages.error(request, f"匯入失敗，找不到產品: {e}")
                    return redirect("purchase_orders:import_file")

            messages.success(request, "成功匯入 CSV")
            return redirect("purchase_orders:index")

        elif file.name.endswith(".xlsx"):
            df = pd.read_excel(file)
            df.rename(
                columns={
                    "序號": "order_number",
                    "供應商名稱": "supplier",
                    "電話": "supplier_tel",
                    "連絡人": "contact_person",
                    "Email": "supplier_email",
                    "產品": "product",
                    "數量": "quantity",
                    "價格": "price",
                    "小計": "subtotal",
                    "總價": "total_amount",
                    "備註": "notes",
                },
                inplace=True,
            )

            for _, row in df.iterrows():
                try:
                    supplier = Supplier.objects.get(id=int(row["supplier"]))
                    product = Product.objects.get(id=int(row["product"]))

                    purchase_order, created = PurchaseOrder.objects.get_or_create(
                        order_number=str(row["order_number"]),
                        supplier=supplier,
                        supplier_tel=str(row["supplier_tel"]),
                        contact_person=str(row["contact_person"]),
                        supplier_email=str(row["supplier_email"]),
                        total_amount=str(row["total_amount"]),
                        notes=str(row["notes"]) if not pd.isna(row["notes"]) else "",
                    )

                    ProductItem.objects.create(
                        purchase_order=purchase_order,
                        product=product,
                        quantity=int(row["quantity"]),
                        price=int(row["price"]),
                        subtotal=int(row["subtotal"]),
                    )

                except Supplier.DoesNotExist as e:
                    messages.error(request, f"匯入失敗，找不到供應商: {e}")
                    continue  # Skip to the next row
                except Product.DoesNotExist as e:
                    messages.error(request, f"匯入失敗，找不到產品: {e}")
                    continue  # Skip to the next row

            messages.success(request, "成功匯入 Excel")
            return redirect("purchase_orders:index")
        else:
            messages.error(request, "匯入失敗(檔案不是 CSV 或 Excel)")
            return render(request, "layouts/import.html", {"form": form})

    form = FileUploadForm()
    return render(request, "layouts/import.html", {"form": form})


def export_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="Purchase_Orders.csv"'

    writer = csv.writer(response)
    writer.writerow(
        [
            "序號",
            "供應商名稱",
            "電話",
            "連絡人",
            "Email",
            "建立時間",
            "刪除時間",
            "產品",
            "數量",
            "價格",
            "小計",
            "總價",
            "備註",
        ]
    )

    purchase_orders = PurchaseOrder.objects.all()

    for purchase_order in purchase_orders:

        product_items = ProductItem.objects.filter(purchase_order=purchase_order)

        for product_item in product_items:
            writer.writerow(
                [
                    purchase_order.order_number,
                    purchase_order.supplier.name,
                    purchase_order.supplier_tel,
                    purchase_order.contact_person,
                    purchase_order.supplier_email,
                    purchase_order.created_at,
                    purchase_order.deleted_at,
                    product_item.product,
                    product_item.quantity,
                    product_item.price,
                    product_item.subtotal,
                    purchase_order.total_amount,
                    purchase_order.notes,
                ]
            )

    return response


def export_excel(request):
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = "attachment; filename=Purchase_Orders.xlsx"

    # 使用 prefetch_related 获取关联的 items
    purchase_orders = (
        PurchaseOrder.objects.select_related("supplier")
        .prefetch_related("items__product")  # 使用 `items` 作为 related_name
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
            "items__price",
            "items__subtotal",
            "total_amount",
            "notes",
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
        "items__product__product_name": "產品",
        "items__quantity": "數量",
        "items__price": "價格",
        "items__subtotal": "小計",
        "total_amount": "總價",
        "notes": "備註",
    }

    df.rename(columns=column_mapping, inplace=True)

    with pd.ExcelWriter(response, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Purchase_Orders")
    return response
