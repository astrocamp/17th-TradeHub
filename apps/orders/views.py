import csv

import pandas as pd
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms.form import OrderForm
from .models import Orders


def index(request):
    state = request.GET.get("select")
    order_by = request.GET.get("sort", "id")
    is_desc = request.GET.get("desc", "True") == "False"

    orders = Orders.objects.all()

    if state in Orders.AVAILABLE_STATES:
        orders = Orders.objects.filter(state=state)
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
    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("orders:index")
    form = OrderForm()
    return render(request, "orders/new.html", {"form": form})


def order_update_and_delete(request, id):
    order = get_object_or_404(Orders, id=id)
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


def export_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="Orders.csv"'

    writer = csv.writer(response)
    writer.writerow(
        ["序號", "客戶名稱", "商品名稱", "備註", "建立時間", "更新時間", "刪除時間"]
    )

    orders = Orders.objects.all()
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

    orders = Orders.objects.select_related("client", "product").values(
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
