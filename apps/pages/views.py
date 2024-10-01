import calendar
from datetime import timedelta
from math import pi

import pandas as pd
from django.db.models import Count, Sum
from django.shortcuts import redirect, render
from django.utils import timezone

from apps.clients.forms.clients_form import ClientForm
from apps.clients.models import Client
from apps.goods_receipts.forms.goods_receipts_form import GoodsReceiptForm
from apps.goods_receipts.models import GoodsReceipt
from apps.inventory.forms.inventory_form import RestockForm
from apps.inventory.models import Inventory
from apps.orders.forms.orders_form import OrderForm
from apps.orders.models import Order
from apps.products.forms import ProductForm
from apps.products.models import Product, Supplier
from apps.purchase_orders.forms.purchase_orders_form import PurchaseOrderForm
from apps.purchase_orders.models import PurchaseOrder
from apps.sales_orders.forms.sales_order_form import SalesOrderForm
from apps.sales_orders.models import SalesOrder
from apps.suppliers.forms.supplier_form import SupplierForm
from apps.suppliers.models import Supplier


def out_home(request):
    return render(request, "pages/out_home.html")


def home(request):
    return render(request, "pages/home.html")


def welcome(request):
    if request.session.get("has_seen_welcome", False):
        return redirect("pages:home")

    request.session["has_seen_welcome"] = True
    return render(request, "pages/welcome.html")


def sales_chart(request):

    # 抓基本資料數值
    clients_num = len(Client.objects.filter(user=request.user).values("name"))
    products_num = len(Product.objects.filter(user=request.user).values("number"))
    suppliers_num = len(Supplier.objects.filter(user=request.user).values("name"))
    inventory_num = Inventory.objects.filter(user=request.user).aggregate(
        total_quantity=Sum("quantity")
    )

    def format_chinese_date(date_obj):
        month = date_obj.month
        day = date_obj.day
        return f"{month}月{day}日"

    now = timezone.now()
    year, month = now.year, now.month

    _, last_day = calendar.monthrange(year, month)
    first_day_of_month = now.replace(day=1)
    last_day_of_month = (first_day_of_month + timedelta(days=32)).replace(
        day=1
    ) - timedelta(days=1)

    first_day_of_month_chinese = format_chinese_date(first_day_of_month)
    last_day_of_month_chinese = format_chinese_date(last_day_of_month)

    clients_month_num = Client.objects.filter(
        user=request.user,
    ).count()

    products_month_num = Product.objects.filter(
        user=request.user,
    ).count()

    suppliers_month_num = Supplier.objects.filter(
        user=request.user,
    ).count()

    inventory_month_num = Inventory.objects.filter(
        user=request.user,
    ).count()

    # 抓訂單類數值
    orders_num = len(Order.objects.values("deleted_at").filter(deleted_at=None))
    orders_progress_num = len(
        Order.objects.values("deleted_at", "state").filter(
            deleted_at=None, state="progress"
        )
    )
    orders_pending_num = len(
        Order.objects.values("deleted_at", "state").filter(
            deleted_at=None, state="to_be_confirmed"
        )
    )
    sales_orders_num = len(
        SalesOrder.objects.values("deleted_at").filter(deleted_at=None)
    )
    sales_orders_progress_num = len(
        SalesOrder.objects.values("deleted_at", "state").filter(
            deleted_at=None, state="progress"
        )
    )
    sales_orders_pending_num = len(
        SalesOrder.objects.values("deleted_at", "state").filter(
            deleted_at=None, state="pending"
        )
    )
    purchase_orders_num = len(
        PurchaseOrder.objects.values("deleted_at").filter(deleted_at=None)
    )
    purchase_orders_progress_num = len(
        PurchaseOrder.objects.values("deleted_at", "state").filter(
            deleted_at=None, state="progress"
        )
    )
    purchase_orders_pending_num = len(
        PurchaseOrder.objects.values("deleted_at", "state").filter(
            deleted_at=None, state="pending"
        )
    )
    goods_receipts_num = len(
        GoodsReceipt.objects.values("deleted_at").filter(deleted_at=None)
    )
    goods_receipts_progress_num = len(
        GoodsReceipt.objects.values("deleted_at", "state").filter(
            deleted_at=None, state="to_be_stocked"
        )
    )
    goods_receipts_pending_num = len(
        GoodsReceipt.objects.values("deleted_at", "state").filter(
            deleted_at=None, state="to_be_restocked"
        )
    )

    # 抓VIP訂單客戶
    vip_clients = (
        Client.objects.annotate(
            total_quantity=Count("orders"), total_amount=Sum("orders__amount")
        )
        .filter(total_quantity__gt=0)
        .order_by("-total_amount")[:5]
    )

    # 圓餅圖
    sales_orders = SalesOrder.objects.all()
    sales_data = (
        sales_orders.values("items__product__product_name")
        .annotate(total_quantity=Sum("items__ordered_quantity"))
        .order_by("-total_quantity")
    )
    data = {
        "product": [item["items__product__product_name"] for item in sales_data],
        "quantity": [item["total_quantity"] for item in sales_data],
    }

    df = pd.DataFrame(data)
    df["percent"] = df["quantity"] / df["quantity"].sum() * 100

    num_products = len(df)

    # 設置顏色
    if num_products == 0:
        df = pd.DataFrame({"product": ["無資料"], "quantity": [1]})
        df["color"] = ["#d9d9d9"]
    else:
        # 顏色調色板
        palette = []
        if num_products == 1:
            palette = ["#1f77b4"]
        elif num_products == 2:
            palette = ["#1f77b4", "#ff7f0e"]
        elif num_products <= 20:
            palette = [
                "#1f77b4",
                "#ff7f0e",
                "#2ca02c",
                "#d62728",
                "#9467bd",
                "#8c564b",
                "#e377c2",
                "#7f7f7f",
                "#bcbd22",
                "#17becf",
            ][:num_products]
        else:
            palette = ["#1f77b4"] * 20  # 或使用其他顏色
            others_sum = df["quantity"].sum() - df["quantity"].head(20).sum()
            df = df.head(20).append(
                pd.DataFrame(
                    {
                        "product": ["其他"],
                        "quantity": [others_sum],
                        "color": ["#d9d9d9"],
                    }
                )
            )

        df["color"] = palette[: len(df)]

        data1 = {
            "product": df["product"].tolist(),
            "quantity": df["quantity"].tolist(),
            "color": df["color"].tolist(),
        }

    content = {
        "clients_num": clients_num,
        "products_num": products_num,
        "suppliers_num": suppliers_num,
        "inventory_num": inventory_num["total_quantity"],
        "orders_num": orders_num,
        "sales_orders_num": sales_orders_num,
        "purchase_orders_num": purchase_orders_num,
        "goods_receipts_num": goods_receipts_num,
        "orders_progress_num": orders_progress_num,
        "orders_pending_num": orders_pending_num,
        "sales_orders_progress_num": sales_orders_progress_num,
        "sales_orders_pending_num": sales_orders_pending_num,
        "purchase_orders_progress_num": purchase_orders_progress_num,
        "purchase_orders_pending_num": purchase_orders_pending_num,
        "goods_receipts_progress_num": goods_receipts_progress_num,
        "goods_receipts_pending_num": goods_receipts_pending_num,
        "clients_month_num": clients_month_num,
        "products_month_num": products_month_num,
        "suppliers_month_num": suppliers_month_num,
        "inventory_month_num": inventory_month_num,
        "vip_clients": vip_clients,
        "first_day_of_month": first_day_of_month_chinese,
        "last_day_of_month": last_day_of_month_chinese,
        "data": {
            "product": df["product"].tolist(),
            "quantity": df["quantity"].tolist(),
            "color": df["color"].tolist(),
        },
    }

    return render(request, "pages/sales_chart.html", content)


def about(request):
    return render(request, "pages/about.html")


def search(request):
    search = request.POST.get("search", "")
    category = request.POST.get("select")

    if category == "Product":
        products = Product.objects.filter(
            product_name__contains=search, user=request.user
        )
        results = []
        for item in products:
            results += [
                (
                    item.number,
                    item.product_name,
                    item.cost_price,
                    item.sale_price,
                    item.supplier,
                    item.note,
                )
            ]
        fields_names = [fields for fields in ProductForm._meta.labels.values()]
    elif category == "Client":
        clients = Client.objects.filter(name__contains=search, user=request.user)
        results = []
        for item in clients:
            results += [
                (
                    item.number,
                    item.name,
                    item.phone_number,
                    item.address,
                    item.email,
                    item.note,
                )
            ]
        fields_names = [fields for fields in ClientForm._meta.labels.values()]
    elif category == "Supplier":
        suppliers = Supplier.objects.filter(name__contains=search, user=request.user)
        results = []
        for item in suppliers:
            results += [
                (
                    item.number,
                    item.name,
                    item.telephone,
                    item.contact_person,
                    item.email,
                    item.gui_number,
                    item.address,
                    item.note,
                )
            ]
        fields_names = [fields for fields in SupplierForm._meta.labels.values()]
    elif category == "Inventory":
        inventory = Inventory.objects.filter(
            product__product_name__contains=search, user=request.user
        )
        results = []
        for item in inventory:
            results += [
                (
                    item.number,
                    item.product,
                    item.supplier,
                    item.quantity,
                    item.safety_stock,
                    item.note,
                )
            ]
        fields_names = [fields for fields in RestockForm._meta.labels.values()]
    elif category == "Order":
        orders = Order.objects.filter(order_number__contains=search, user=request.user)
        results = []
        for order in orders:
            results += [
                (
                    order.order_number,
                    order.client,
                    order.client_tel,
                    order.client_address,
                    order.client_email,
                    order.note,
                    order.amount,
                )
            ]
        fields_names = [fields for fields in OrderForm._meta.labels.values()]
    elif category == "PurchaseOrder":
        purchase = PurchaseOrder.objects.filter(
            order_number__contains=search, user=request.user
        )
        results = []
        for order in purchase:
            results += [
                (
                    order.order_number,
                    order.supplier,
                    order.supplier_tel,
                    order.contact_person,
                    order.supplier_email,
                    order.amount,
                    order.note,
                )
            ]
        fields_names = [fields for fields in PurchaseOrderForm._meta.labels.values()]
    elif category == "SalesOrder":
        purchase = SalesOrder.objects.filter(
            order_number__contains=search, user=request.user
        )
        results = []
        for order in purchase:
            results += [
                (
                    order.order_number,
                    order.client,
                    order.client_tel,
                    order.client_address,
                    order.client_email,
                    order.shipping_method,
                    order.amount,
                    order.note,
                )
            ]
        fields_names = [fields for fields in SalesOrderForm._meta.labels.values()]
    elif category == "GoodsReceipt":
        purchase = GoodsReceipt.objects.filter(
            order_number__contains=search, user=request.user
        )
        results = []
        for order in purchase:
            results += [
                (
                    order.order_number,
                    order.supplier.name,
                    order.supplier_tel,
                    order.contact_person,
                    order.supplier_email,
                    order.receiving_method,
                    order.amount,
                    order.note,
                )
            ]
        fields_names = [fields for fields in GoodsReceiptForm._meta.labels.values()]

    content = {
        "search": search,
        "category": category,
        "results": results,
        "fields_names": fields_names,
    }
    return render(request, "pages/results.html", content)
