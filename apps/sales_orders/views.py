import csv
from datetime import datetime, timedelta, timezone

import pandas as pd
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from apps.clients.models import Client
from apps.inventory.models import Inventory
from apps.products.models import Product
from apps.sales_orders.models import SalesOrder

from .forms.sales_order_form import FileUploadForm, SalesOrderForm
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

                    client = Client.objects.get(id=row[0])
                    product = Product.objects.get(id=row[1])
                    stock = Inventory.objects.get(id=row[3])
                    SalesOrder.objects.create(
                        client=client,
                        product=product,
                        quantity=row[2],
                        stock=stock,
                        price=row[4],
                    )

                messages.success(request, "成功匯入 CSV")
                return redirect("sales_orders:index")

            elif file.name.endswith(".xlsx"):
                df = pd.read_excel(file)
                df.rename(
                    columns={
                        "客戶": "client",
                        "商品": "product",
                        "數量": "quantity",
                        "庫存": "stock",
                        "價位": "price",
                    },
                    inplace=True,
                )
                for _, row in df.iterrows():

                    client = Client.objects.get(id=int(row["client"]))
                    product = Product.objects.get(id=int(row["product"]))
                    stock = Inventory.objects.get(id=int(row["stock"]))
                    SalesOrder.objects.create(
                        client=client,
                        product=product,
                        quantity=str(row["quantity"]),
                        stock=stock,
                        price=str(row["price"]),
                    )

                messages.success(request, "成功匯入 Excel")
                return redirect("sales_orders:index")

            else:
                messages.error(request, "匯入失敗(檔案不是 CSV 或 Excel)")
                return render(request, "layouts/import.html", {"form": form})

    form = FileUploadForm()
    return render(request, "layouts/import.html", {"form": form})


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


@receiver(pre_save, sender=SalesOrder)
def update_stats(sender, instance, **kwargs):
    time_now = datetime.now(timezone(timedelta(hours=+8))).strftime("%Y/%m/%d %H:%M:%S")
    if instance.quantity > instance.stock.quantity:
        instance.set_pending()
    elif instance.quantity < instance.stock.quantity:
        instance.set_progress()
        if instance.is_finished:
            inventory = Inventory.objects.get(id=instance.stock.id)
            inventory.quantity -= instance.quantity
            inventory.note += f"{time_now} 扣除庫存{instance.quantity}\n"
            inventory.save()
            instance.set_finished()
            instance.is_finished = True


def transform(request, id):
    sales_order = get_object_or_404(SalesOrder, id=id)
    sales_order.is_finished = True
    sales_order.save()
    messages.success(request, "扣除庫存完成!")
    return redirect("sales_orders:index")
