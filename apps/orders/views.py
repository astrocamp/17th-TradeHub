import csv

import pandas as pd
from django.contrib import messages
from django.core.paginator import Paginator
from django.forms import inlineformset_factory
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.clients.models import Client
from apps.products.models import Product

from .forms.orders_form import (
    FileUploadForm,
    OrderForm,
    OrderProductItemForm,
    OrderProductItemFormSet,
)
from .models import Order, OrderProductItem


def index(request):
    state = request.GET.get("select")
    order_by = request.GET.get("sort", "id")
    is_desc = request.GET.get("desc", "True") == "False"

    orders = Order.objects.all()

    if state in Order.AVAILABLE_STATES:
        orders = Order.objects.filter(state=state)
    order_by_field = order_by if is_desc else "-" + order_by
    orders = orders.order_by(order_by_field)

    paginator = Paginator(orders, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    content = {
        "state": state,
        "order_by": order_by,
        "is_desc": is_desc,
        "orders": page_obj,
        "page_obj": page_obj,
    }

    return render(request, "orders/index.html", content)


def new(request):
    new_order_number = generate_order_number()
    if request.method == "POST":
        form = OrderForm(request.POST)
        formset = OrderProductItemFormSet(request.POST, instance=form.instance)
        if form.is_valid() and formset.is_valid():
            order = form.save(commit=False)
            order.order_number = new_order_number
            order.username = request.user.username
            order.save()
            formset.instance = order
            formset.save()
            return redirect("orders:index")
        else:
            return render(
                request, "orders/new.html", {"form": form, "formset": formset}
            )
    form = OrderForm()
    formset = OrderProductItemFormSet(instance=form.instance)
    return render(
        request,
        "orders/new.html",
        {"form": form, "formset": formset},
    )


def show(request, id):
    order = get_object_or_404(Order, pk=id)
    product_items = OrderProductItem.objects.filter(order=order)
    return render(
        request,
        "orders/show.html",
        {"order": order, "product_items": product_items},
    )


def order_update_and_delete(request, id):
    order = get_object_or_404(Order, id=id)
    if request.method == "POST":
        if "delete" in request.POST:
            order.delete()
            messages.success(request, "刪除完成!")
            return redirect("orders:index")
        else:
            form = OrderForm(request.POST, instance=order)
            if form.is_valid():
                form.save()
                return redirect("orders:index")
    form = OrderForm(instance=order)
    return render(request, "orders/edit.html", {"order": order, "form": form})


def edit(request, id):
    order = get_object_or_404(Order, pk=id)
    if request.method == "POST":
        form = OrderForm(request.POST, instance=order)
        formset = OrderProductItemFormSet(request.POST, instance=order)

        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect("orders:show", order.id)
        return render(
            request,
            "orders/edit.html",
            {"order": order, "form": form, "formset": formset},
        )
    form = OrderForm(instance=order)
    formset = get_product_item_formset(0)(instance=order)
    return render(
        request,
        "orders/edit.html",
        {"order": order, "form": form, "formset": formset},
    )


def delete(request, id):
    order = get_object_or_404(Order, pk=id)
    order.delete()
    messages.success(request, "刪除完成!")
    return redirect("purchase_orders:index")


def get_product_item_formset(extra):
    return inlineformset_factory(
        Order,
        OrderProductItem,
        form=OrderProductItemForm,
        extra=extra,
        can_delete=True,
    )


def load_client_info(request):
    client_id = request.GET.get("client_id")
    client = Client.objects.get(id=client_id)
    data = {
        "client_tel": client.phone_number,
        "client_address": client.address,
        "client_email": client.email,
    }
    return JsonResponse(data)


def load_product_info(request):
    product_id = request.GET.get("id")
    product = Product.objects.get(id=product_id)
    return JsonResponse({"sale_price": product.sale_price})


def generate_order_number():
    today = timezone.localtime().strftime("%Y%m%d")
    last_order = (
        Order.all_objects.filter(order_number__startswith=today)
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
                next(reader)  # Skip header row

                for row in reader:
                    try:
                        client = Client.objects.get(id=row[1])
                        product = Product.objects.get(id=row[2])

                        Order.objects.create(
                            code=row[0],
                            client=client,
                            product=product,
                            note=row[3],
                        )
                    except (Client.DoesNotExist, Product.DoesNotExist) as e:
                        messages.error(request, f"匯入失敗，找不到客戶或商品: {e}")
                        return redirect("orders:index")

                messages.success(request, "成功匯入 CSV")
                return redirect("orders:index")

            elif file.name.endswith(".xlsx"):
                df = pd.read_excel(file)
                df.rename(
                    columns={
                        "序號": "code",
                        "客戶名稱": "client",
                        "商品名稱": "product",
                        "備註": "note",
                    },
                    inplace=True,
                )
                for _, row in df.iterrows():
                    try:
                        client = Client.objects.get(id=int(row["client"]))
                        product = Product.objects.get(id=int(row["product"]))

                        Order.objects.create(
                            code=str(row["code"]),
                            client=client,
                            product=product,
                            note=str(row["note"]) if not pd.isna(row["note"]) else "",
                        )
                    except (Client.DoesNotExist, Product.DoesNotExist) as e:
                        messages.error(request, f"匯入失敗，找不到客戶或商品: {e}")
                        return redirect("orders:index")

                messages.success(request, "成功匯入 Excel")
                return redirect("orders:index")

            else:
                messages.error(request, "匯入失敗(檔案不是 CSV 或 Excel)")
                return render(request, "layouts/import.html", {"form": form})

    form = FileUploadForm()
    return render(request, "layouts/import.html", {"form": form})


def export_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="Orders.csv"'

    writer = csv.writer(response)
    writer.writerow(
        ["序號", "客戶名稱", "商品名稱", "備註", "建立時間", "更新時間", "刪除時間"]
    )

    orders = Order.objects.all()
    for order in orders:
        writer.writerow(
            [
                order.code,
                order.client,
                order.product,
                order.note,
                order.created_at,
                order.updated_at,
                order.deleted_at,
            ]
        )
    return response


def export_excel(request):
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = "attachment; filename=Orders.xlsx"

    orders = Order.objects.select_related("client", "product").values(
        "code",
        "client__name",
        "product__product_name",
        "note",
        "created_at",
        "updated_at",
        "deleted_at",
    )

    df = pd.DataFrame(orders)
    for col in df.select_dtypes(include=["datetime64[ns, UTC]"]).columns:
        df[col] = df[col].dt.strftime("%Y-%m-%d %H:%M:%S")

    column_mapping = {
        "code": "序號",
        "client__name": "客戶名稱",
        "product__product_name": "商品名稱",
        "note": "備註",
        "created_at": "建立時間",
        "updated_at": "更新時間",
        "deleted_at": "刪除時間",
    }

    df.rename(columns=column_mapping, inplace=True)

    with pd.ExcelWriter(response, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Orders")

    return response
