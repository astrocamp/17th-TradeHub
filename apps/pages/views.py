from datetime import timedelta
from math import pi

import pandas as pd
from bokeh.embed import components
from bokeh.models import ColumnDataSource
from bokeh.palettes import Category20c
from bokeh.plotting import figure
from bokeh.resources import CDN
from bokeh.transform import cumsum
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
from apps.suppliers.forms.form import SupplierForm


def out_home(request):
    return render(request, "pages/out_home.html")


def home(request):
    if request.user.first_login:
        request.user.first_login = False
        request.user.save()
        return render(request, "pages/welcome.html", {"first_login": True})
    return render(request, "pages/home.html")


def welcome(request):
    if request.session.get("has_seen_welcome", False):
        return redirect("pages:home")

    request.session["has_seen_welcome"] = True
    return render(request, "pages/welcome.html")


def search(request):
    search = request.POST.get("search", "")
    category = request.POST.get("select")

    if category == "Product":
        products = Product.objects.filter(product_name__contains=search)
        results = [fields[:-3] for fields in products.values_list()]
        fields_names = [fields for fields in ProductForm._meta.labels.values()]
    elif category == "Client":
        clients = Client.objects.filter(name__contains=search)
        results = [fields[:5] for fields in clients.values_list()]
        fields_names = [fields for fields in ClientForm._meta.labels.values()]
    elif category == "Supplier":
        suppliers = Supplier.objects.filter(name__contains=search)
        results = [fields[:7] for fields in suppliers.values_list()]
        fields_names = [fields for fields in SupplierForm._meta.labels.values()]
    elif category == "Inventory":
        inventory = Inventory.objects.filter(product__product_name__contains=search)
        results = []
        for item in inventory:
            results += [
                (
                    item.id,
                    item.product,
                    item.supplier,
                    item.quantity,
                    item.safety_stock,
                    item.note,
                )
            ]
        fields_names = [fields for fields in RestockForm._meta.labels.values()]
    elif category == "Order":
        orders = Order.objects.filter(order_number__contains=search)
        results = []
        for order in orders:
            results += [
                (
                    order.id,
                    order.order_number,
                    order.client.name,
                    order.client_tel,
                    order.client_address,
                    order.client_email,
                    order.username,
                )
            ]
        fields_names = [fields for fields in OrderForm._meta.labels.values()]
    elif category == "PurchaseOrder":
        purchase = PurchaseOrder.objects.filter(order_number__contains=search)
        results = []
        for order in purchase:
            results += [
                (
                    order.id,
                    order.order_number,
                    order.supplier.name,
                    order.supplier_tel,
                    order.supplier_email,
                    order.amount,
                    order.note,
                )
            ]
        fields_names = [fields for fields in PurchaseOrderForm._meta.labels.values()]
    elif category == "SalesOrder":
        purchase = SalesOrder.objects.filter(order_number__contains=search)
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
                    order.note,
                )
            ]
        fields_names = [fields for fields in SalesOrderForm._meta.labels.values()]
    elif category == "GoodsReceipt":
        purchase = GoodsReceipt.objects.filter(order_number__contains=search)
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


def sales_chart(request):

    # 抓基本資料數值
    clients_num = len(Client.objects.values("name"))
    products_num = len(Product.objects.values("product_number"))
    suppliers_num = len(Supplier.objects.values("name"))
    inventory_num = Inventory.objects.aggregate(total_quantity=Sum("quantity"))

    def arabic_to_chinese(num):
        chinese_digits = {
            "0": "十",
            "1": "一",
            "2": "二",
            "3": "三",
            "4": "四",
            "5": "五",
            "6": "六",
            "7": "七",
            "8": "八",
            "9": "九",
        }
        return "".join(chinese_digits[digit] for digit in str(num))

    def format_chinese_date(date_obj):
        month = arabic_to_chinese(date_obj.month)
        day = arabic_to_chinese(date_obj.day)
        return f"{month}月{day}日"

    now = timezone.now()
    first_day_of_month = now.replace(day=1)
    last_day_of_month = (first_day_of_month + timedelta(days=32)).replace(
        day=1
    ) - timedelta(days=1)

    first_day_of_month_chinese = format_chinese_date(first_day_of_month)
    last_day_of_month_chinese = format_chinese_date(last_day_of_month)

    clients_month_num = Client.objects.filter(
        created_at__range=(first_day_of_month, last_day_of_month),
        deleted_at=None,
    ).count()

    products_month_num = Product.objects.filter(
        created_at__range=(first_day_of_month, last_day_of_month),
        deleted_at=None,
    ).count()

    suppliers_month_num = Supplier.objects.filter(
        created_at__range=(first_day_of_month, last_day_of_month),
        deleted_at=None,
    ).count()

    inventory_month_num = Inventory.objects.filter(
        created_at__range=(first_day_of_month, last_day_of_month),
        deleted_at=None,
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

    # 做圓餅圖表
    sales_orders = SalesOrder.objects.all()
    sales_data = (
        sales_orders.values("items__product__product_name")
        .annotate(total_quantity=Sum("items__ordered_quantity"))
        .order_by("-total_quantity")
    )

    data = {
        "product": [item["items__product__product_name"] for item in sales_data],
        "quantity": [item["items__ordered_quantity"] for item in sales_data],
    }

    df = pd.DataFrame(data)
    df["angle"] = df["quantity"] / df["quantity"].sum() * 2 * pi

    num_products = len(df)

    if num_products == 0:
        df = pd.DataFrame({"product": ["無資料"], "quantity": [1]})
        df["angle"] = [2 * pi]
        df["color"] = ["#d9d9d9"]
    else:
        if num_products == 1:
            palette = ["#1f77b4"]
        elif num_products == 2:
            palette = ["#1f77b4", "#ff7f0e"]
        elif num_products <= 20:
            palette = Category20c[num_products]
        else:
            palette = Category20c[20]

            top_20 = df[:20]
            others = df[20:]

            other_sum = others["quantity"].sum()
            top_20 = top_20.append(
                pd.DataFrame(
                    {
                        "product": ["其他"],
                        "quantity": [other_sum],
                        "angle": [other_sum / df["quantity"].sum() * 2 * pi],
                    }
                )
            )

            palette.append("#d9d9d9")
            df = top_20

        df["color"] = palette[: len(df)]

    source1 = ColumnDataSource(df)

    p1 = figure(
        title="熱銷商品",
        width=600,
        height=300,
        tools="pan,wheel_zoom,box_zoom,reset",
        toolbar_location="above",
    )

    p1.wedge(
        x=0,
        y=1,
        radius=0.4,
        start_angle=cumsum("angle", include_zero=True),
        end_angle=cumsum("angle"),
        line_color="white",
        fill_color="color",
        legend_field="product",
        source=source1,
    )

    p1.grid.grid_line_color = None
    p1.axis.visible = False
    p1.legend.location = "top_left"
    p1.legend.label_text_font_size = "10pt"

    script1, div1 = components(p1)

    bokeh_js = CDN.js_files[0]
    bokeh_css = CDN.css_files[0] if CDN.css_files else None

    content = {
        "clients_num": clients_num,
        "products_num": products_num,
        "suppliers_num": suppliers_num,
        "inventory_num": inventory_num["total_quantity"],
        "orders_num": orders_num,
        "sales_orders_num": sales_orders_num,
        "purchase_orders_num": purchase_orders_num,
        "goods_receipts_num": goods_receipts_num,
        "script1": script1,
        "div1": div1,
        "bokeh_js": bokeh_js,
        "bokeh_css": bokeh_css,
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
    }

    return render(request, "pages/sales_chart.html", content)
