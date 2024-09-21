import csv

import pandas as pd
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms.sales_order_form import SalesOrderForm
from .models import SalesOrder


def index(request):
    state = request.GET.get("select")
    order_by = request.GET.get("sort", "id")
    is_desc = request.GET.get("desc", "True") == "False"

    sales_orders = SalesOrder.objects.all()

    if state in SalesOrder.AVAILABLE_STATES:
        sales_orders = SalesOrder.objects.filter(state=state)
    order_by_field = order_by if is_desc else "-" + order_by
    sales_orders = sales_orders.order_by(order_by_field)
    paginator = Paginator(sales_orders, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    content = {
        "sales_orders": page_obj,
        "selected_state": state,
        "is_desc": is_desc,
        "order_by": order_by,
        "page_obj": page_obj,
    }

    return render(request, "sales_orders/index.html", content)


def new(request):
    if request.method == "POST":
        form = SalesOrderForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("sales_orders:index")
    else:
        form = SalesOrderForm()
    return render(request, "sales_orders/new.html", {"form": form})


def edit(request, id):
    sales_orders = get_object_or_404(SalesOrder, id=id)
    if request.method == "POST":
        form = SalesOrderForm(request.POST, instance=sales_orders)
        if form.is_valid():
            form.save()
            return redirect("sales_orders:index")
    else:
        form = SalesOrderForm(instance=sales_orders)

    return render(
        request,
        "sales_orders/edit.html",
        {"sales_orders": sales_orders, "form": form},
    )


def delete(request, id):
    sales_orders = get_object_or_404(SalesOrder, id=id)
    sales_orders.delete()
    messages.success(request, "刪除完成!")
    return redirect("sales_orders:index")


def export_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="SalesOrders.csv"'

    writer = csv.writer(response)
    writer.writerow(
        [
            "客戶",
            "商品",
            "數量",
            "庫存",
            "價位",
            "建立時間",
            "更新時間",
            "刪除時間",
        ]
    )

    sales_orders = SalesOrder.objects.all()
    for sales_order in sales_orders:
        writer.writerow(
            [
                sales_order.client,
                sales_order.product,
                sales_order.quantity,
                sales_order.stock,
                sales_order.price,
                sales_order.created_at,
                sales_order.last_updated,
                sales_order.deleted_at,
            ]
        )

    return response


def export_excel(request):
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = "attachment; filename=SalesOrders.xlsx"

    sales_orders = SalesOrder.objects.select_related(
        "client", "product", "stock"
    ).values(
        "client__name",
        "product__product_name",
        "quantity",
        "stock__state",
        "price",
        "created_at",
        "last_updated",
        "deleted_at",
    )

    df = pd.DataFrame(sales_orders)
    for col in df.select_dtypes(include=["datetime64[ns, UTC]"]).columns:
        df[col] = df[col].dt.strftime("%Y-%m-%d %H:%M:%S")

    column_mapping = {
        "client__name": "客戶",
        "product__product_name": "商品",
        "quantity": "數量",
        "stock__state": "庫存",
        "price": "價位",
        "created_at": "建立時間",
        "last_updated": "更新時間",
        "deleted_at": "刪除時間",
    }

    df.rename(columns=column_mapping, inplace=True)

    with pd.ExcelWriter(response, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="SalesOrders")
    return response
