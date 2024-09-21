import csv

import pandas as pd
from django.contrib import messages
from django.core.paginator import Paginator
from django.forms import inlineformset_factory
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.clients.models import Client
from apps.inventory.models import Inventory
from apps.products.models import Product

from .forms.sales_order_form import (
    SalesOrderForm,
    SalesOrderProductItemForm,
    SalesOrderProductItemFormSet,
)
from .models import SalesOrder, SalesOrderProductItem


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
    new_order_number = generate_order_number()
    if request.method == "POST":
        form = SalesOrderForm(request.POST)
        formset = SalesOrderProductItemFormSet(request.POST, instance=form.instance)
        if form.is_valid() and formset.is_valid():
            order = form.save(commit=False)
            order.order_number = new_order_number
            order.username = request.user.username
            order.save()
            formset.instance = order
            formset.save()
            return redirect("sales_orders:index")
        else:
            return render(
                request, "sales_orders/new.html", {"form": form, "formset": formset}
            )
    form = SalesOrderForm()
    formset = SalesOrderProductItemFormSet(instance=form.instance)
    return render(
        request,
        "sales_orders/new.html",
        {"form": form, "formset": formset},
    )


def show(request, id):
    sales_order = get_object_or_404(SalesOrder, pk=id)
    product_items = SalesOrderProductItem.objects.filter(sales_order=sales_order)
    return render(
        request,
        "orders/show.html",
        {"sales_order": sales_order, "product_items": product_items},
    )


def edit(request, id):
    sales_order = get_object_or_404(SalesOrder, pk=id)
    if request.method == "POST":
        form = SalesOrderForm(request.POST, instance=sales_order)
        formset = SalesOrderProductItemFormSet(request.POST, instance=sales_order)

        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect("sales_orders:show", sales_order.id)
        return render(
            request,
            "sales_orders/edit.html",
            {"sales_order": sales_order, "form": form, "formset": formset},
        )
    form = SalesOrderForm(instance=sales_order)
    formset = get_product_item_formset(0)(instance=sales_order)
    return render(
        request,
        "sales_orders/edit.html",
        {"sales_order": sales_order, "form": form, "formset": formset},
    )


def delete(request, id):
    sales_order = get_object_or_404(SalesOrder, pk=id)
    sales_order.delete()
    messages.success(request, "刪除完成!")
    return redirect("sales_orders:index")


def get_product_item_formset(extra):
    return inlineformset_factory(
        SalesOrder,
        SalesOrderProductItem,
        form=SalesOrderProductItemForm,
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
        SalesOrder.all_objects.filter(order_number__startswith=today)
        .order_by("-order_number")
        .first()
    )

    if last_order:
        last_order_number = int(last_order.order_number[-3:])
        new_order_number = f"{last_order_number + 1:03d}"
    else:
        new_order_number = "001"

    return f"{today}{new_order_number}"


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
