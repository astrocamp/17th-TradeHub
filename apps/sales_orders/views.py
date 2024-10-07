import csv
import random
import string
from datetime import datetime, timedelta
from datetime import timezone as tz

import pandas as pd
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.forms import inlineformset_factory
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.clients.models import Client
from apps.inventory.models import Inventory
from apps.products.models import Product
from apps.sales_orders.forms.sales_order_form import (
    SalesOrderForm,
    SalesOrderProductItemForm,
    SalesOrderProductItemFormSet,
)
from apps.sales_orders.models import SalesOrder, SalesOrderProductItem


def index(request):
    state = request.GET.get("select")
    order_by = request.GET.get("sort", "id")
    is_desc = request.GET.get("desc", "True") == "False"

    sales_orders = SalesOrder.objects.filter(user=request.user)

    if state in SalesOrder.AVAILABLE_STATES:
        sales_orders = SalesOrder.objects.filter(state=state, user=request.user)
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
        formset = SalesOrderProductItemFormSet(request.POST, instance=form.instance)
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
    sales_order = get_object_or_404(SalesOrder, id=id)
    product_items = SalesOrderProductItem.objects.filter(sales_order=sales_order)
    return render(
        request,
        "sales_orders/show.html",
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
            messages.success(request, "更新完成!")
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
    try:
        sales_order.delete()
        messages.success(request, "刪除完成!")
        return redirect("sales_orders:index")
    except:
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
    response["Content-Disposition"] = "attachment; filename=SalesOrders.xlsx"

    sales_orders = (
        SalesOrder.objects.filter(user=request.user)
        .prefetch_related("items")
        .values(
            "client__name",
            "client_tel",
            "client_address",
            "client_email",
            "items__product__product_name",
            "items__ordered_quantity",
            "items__shipped_quantity",
            "items__stock_quantity__state",  # Assuming Inventory model has a state field
            "items__sale_price",
            "created_at",
            "updated_at",
        )
    )

    # Prepare the data for DataFrame
    data = []
    for sales_order in sales_orders:
        data.append(
            [
                sales_order["client__name"],
                sales_order["client_tel"],
                sales_order["client_address"],
                sales_order["client_email"],
                sales_order.get("items__product__product_name", ""),
                sales_order.get("items__ordered_quantity", ""),
                sales_order.get("items__shipped_quantity", ""),
                sales_order.get("items__stock_quantity__state", ""),
                sales_order.get("items__sale_price", ""),
                sales_order["created_at"].strftime("%Y-%m-%d %H:%M:%S"),
                sales_order["updated_at"].strftime("%Y-%m-%d %H:%M:%S"),
            ]
        )

    df = pd.DataFrame(
        data,
        columns=[
            "客戶",
            "客戶電話",
            "客戶地址",
            "客戶Email",
            "商品",
            "訂購數量",
            "實發數量",
            "庫存狀態",
            "價位",
            "建立時間",
            "更新時間",
        ],
    )

    with pd.ExcelWriter(response, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="SalesOrders")

    return response


@receiver(post_save, sender=SalesOrder)
def update_stats(sender, instance, **kwargs):
    time_now = datetime.now(tz(timedelta(hours=+8))).strftime("%Y/%m/%d %H:%M:%S")
    order_items = SalesOrderProductItem.objects.filter(sales_order=instance)

    post_save.disconnect(update_stats, sender=SalesOrder)
    for item in order_items:
        if item.ordered_quantity > item.stock_quantity.quantity:
            instance.set_pending()
            instance.save()

        elif item.ordered_quantity <= item.stock_quantity.quantity:
            instance.set_progress()
            instance.save()

            if instance.is_finished:
                inventory = Inventory.objects.get(id=item.stock_quantity.id)
                inventory.quantity -= item.shipped_quantity
                inventory.note += f"扣除庫存:{item.shipped_quantity}，{time_now}"
                item.shipped_quantity = 0
                inventory.save()
                item.save()
                instance.set_finished()
                instance.save()

    instance.is_finished = False
    instance.save()
    post_save.connect(update_stats, sender=SalesOrder)


def transform(request, id):
    sales_order = get_object_or_404(SalesOrder, id=id)
    sales_order.is_finished = True
    post_save.send(sender=SalesOrder, instance=sales_order, created=False)
    messages.success(request, "扣除庫存完成!")
    return redirect("sales_orders:index")
