import csv
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
from apps.products.models import Product
from apps.sales_orders.models import SalesOrder, SalesOrderProductItem

from .forms.orders_form import OrderForm, OrderProductItemForm, OrderProductItemFormSet
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
        "orders": page_obj,
        "selected_state": state,
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
    return redirect("orders:index")


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


@receiver(post_save, sender=Order)
def update_state(sender, instance, **kwargs):
    time_now = datetime.now(tz(timedelta(hours=+8))).strftime("%Y/%m/%d %H:%M:%S")
    order_items = OrderProductItem.objects.filter(order=instance)

    for item in order_items:
        if instance.is_finished:
            order = SalesOrder.objects.create(
                order_number=generate_order_number(),
                client=instance.client,
                client_tel=instance.client_tel,
                client_address=instance.client_address,
                client_email=instance.client_email,
                amount=instance.amount,
                note=f"轉銷貨單{time_now}",
            )
            SalesOrderProductItem.objects.create(
                sales_order=order,
                product=item.product,
                ordered_quantity=item.ordered_quantity,
                sale_price=item.sale_price,
                shipped_quantity=0,
                subtotal=item.subtotal,
                stock_quantity=item.stock_quantity,
            )
            instance.note = f"{time_now}已轉銷貨單"
            instance.is_finished = False
            instance.set_finished()

    ordered_quantity = [item.ordered_quantity for item in order_items]
    stock_quantity = [item.stock_quantity.quantity for item in order_items]
    order_zip_stock = zip(ordered_quantity, stock_quantity)
    quantity_bool = [quantity[0] > quantity[1] for quantity in order_zip_stock]

    post_save.disconnect(update_state, sender=Order)
    if True in quantity_bool:
        instance.set_to_be_confirmed()
        instance.save()
    else:
        instance.set_progress()
        instance.save()
    post_save.connect(update_state, sender=Order)


def transform_sales_order(request, id):
    order = get_object_or_404(Order, id=id)
    order.is_finished = True
    post_save.send(sender=Order, instance=order, created=True)
    messages.success(request, "轉銷貨單完成!")
    return redirect("orders:index")
