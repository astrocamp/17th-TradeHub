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
from apps.products.models import Product
from apps.sales_orders.models import SalesOrder, SalesOrderProductItem

from .forms.orders_form import OrderForm, OrderProductItemForm, OrderProductItemFormSet
from .models import Order, OrderProductItem


def index(request):
    state = request.GET.get("select")
    order_by = request.GET.get("sort", "id")
    is_desc = request.GET.get("desc", "True") == "False"

    orders = Order.objects.filter(user=request.user)

    if state in Order.AVAILABLE_STATES:
        orders = Order.objects.filter(state=state, user=request.user)
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
    if request.method == "POST":
        form = OrderForm(request.POST, user=request.user)
        formset = OrderProductItemFormSet(
            request.POST, user=request.user, instance=form.instance
        )
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
            return redirect("orders:index")
        else:
            return render(
                request, "orders/new.html", {"form": form, "formset": formset}
            )
    form = OrderForm(user=request.user)
    formset = OrderProductItemFormSet(instance=form.instance, user=request.user)
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
            messages.success(request, "更新完成!")
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
    try:
        order.delete()
        messages.success(request, "刪除完成!")
        return redirect("orders:index")
    except:
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
    response["Content-Disposition"] = "attachment; filename=Orders.xlsx"

    orders = (
        Order.objects.filter(user=request.user)
        .select_related("client")
        .prefetch_related("items")
        .values(
            "order_number",
            "client__name",
            "client_tel",
            "client_address",
            "client_email",
            "items__product__product_name",
            "items__ordered_quantity",
            "note",
            "created_at",
            "updated_at",
        )
    )
    data = []
    for order in orders:
        data.append(
            [
                order["order_number"],
                order["client__name"],
                order["client_tel"],
                order["client_address"],
                order["client_email"],
                order.get("items__product__product_name", ""),
                order.get("items__ordered_quantity", ""),
                order["note"],
                order["created_at"],
                order["updated_at"],
            ]
        )

    df = pd.DataFrame(
        data,
        columns=[
            "序號",
            "客戶名稱",
            "客戶電話",
            "客戶地址",
            "客戶Email",
            "商品名稱",
            "數量",
            "備註",
            "建立時間",
            "更新時間",
        ],
    )

    for col in df.select_dtypes(include=["datetime64[ns, UTC]"]).columns:
        df[col] = df[col].dt.strftime("%Y-%m-%d %H:%M:%S")

    with pd.ExcelWriter(response, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Orders")

    return response


@receiver(post_save, sender=Order)
def update_state(sender, instance, **kwargs):
    time_now = datetime.now(tz(timedelta(hours=+8))).strftime("%Y/%m/%d %H:%M:%S")
    order_items = OrderProductItem.objects.filter(order=instance)

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

    if instance.is_finished:
        order = SalesOrder.objects.create(
            order_number=generate_order_number(instance),
            client=instance.client,
            client_tel=instance.client_tel,
            client_address=instance.client_address,
            client_email=instance.client_email,
            username=instance.username,
            amount=0,
            note=f"轉銷貨單{time_now}",
            user=instance.user,
        )
        for item in order_items:
            SalesOrderProductItem.objects.create(
                sales_order=order,
                product=item.product,
                ordered_quantity=item.ordered_quantity,
                sale_price=item.sale_price,
                shipped_quantity=0,
                subtotal=item.subtotal,
                stock_quantity=item.stock_quantity,
                user=instance.user,
            )
        instance.note = f"{time_now}已轉銷貨單"
        instance.is_finished = False
        instance.set_finished()
        instance.save()
    post_save.connect(update_state, sender=Order)


def transform_sales_order(request, id):
    order = get_object_or_404(Order, id=id)
    order.is_finished = True
    post_save.send(sender=Order, instance=order, created=False)
    messages.success(request, "轉銷貨單完成!")
    return redirect("orders:index")
