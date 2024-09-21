from datetime import timedelta
from math import pi

import pandas as pd
from bokeh.embed import components
from bokeh.models import ColumnDataSource
from bokeh.palettes import Category20c
from bokeh.plotting import figure
from bokeh.resources import CDN
from bokeh.transform import cumsum
from django.db.models import Sum
from django.shortcuts import render
from django.utils import timezone

from apps.clients.models import Client
from apps.goods_receipts.models import GoodsReceipt
from apps.inventory.models import Inventory
from apps.orders.models import Orders
from apps.products.models import Product, Supplier
from apps.purchase_orders.models import PurchaseOrder
from apps.sales_orders.models import SalesOrder


def sales_chart(request):

    sales_orders = SalesOrder.objects.all()
    orders_num = len(Orders.objects.values("deleted_at").filter(deleted_at=None))
    orders_progress_num = len(
        Orders.objects.values("deleted_at", "state").filter(
            deleted_at=None, state="progress"
        )
    )
    orders_pending_num = len(
        Orders.objects.values("deleted_at", "state").filter(
            deleted_at=None, state="pending"
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
            deleted_at=None, state="progress"
        )
    )
    goods_receipts_pending_num = len(
        GoodsReceipt.objects.values("deleted_at", "state").filter(
            deleted_at=None, state="pending"
        )
    )

    clients_num = len(Client.objects.values("name"))
    products_num = len(Product.objects.values("product_number"))
    suppliers_num = len(Supplier.objects.values("name"))
    inventory_num = Inventory.objects.aggregate(total_quantity=Sum("quantity"))

    now = timezone.now()
    first_day_of_month = now.replace(day=1)
    last_day_of_month = (first_day_of_month + timedelta(days=32)).replace(
        day=1
    ) - timedelta(days=1)

    clients_month_num = Client.objects.filter(
        create_at__range=(first_day_of_month, last_day_of_month),
        deleted_at=None,
    ).count()

    products_month_num = Product.objects.filter(
        create_at__range=(first_day_of_month, last_day_of_month),
        deleted_at=None,
    ).count()

    suppliers_month_num = Supplier.objects.filter(
        established_date__range=(first_day_of_month, last_day_of_month),
        deleted_at=None,
    ).count()

    inventory_month_num = Inventory.objects.filter(
        create_at__range=(first_day_of_month, last_day_of_month),
        deleted_at=None,
    ).count()

    vip_clients = len(Client.objects.values("name"))

    clients_name = len(Client.objects.values("name"))

    sales_data = (
        sales_orders.values("product__product_name")
        .annotate(total_quantity=Sum("quantity"))
        .order_by("-total_quantity")
    )

    data = {
        "product": [item["product__product_name"] for item in sales_data],
        "quantity": [item["total_quantity"] for item in sales_data],
    }
    df = pd.DataFrame(data)
    df["angle"] = df["quantity"] / df["quantity"].sum() * 2 * pi
    num_products = len(df)
    if num_products == 0:
        df = pd.DataFrame({"product": ["無資料"], "quantity": [1]})
        df["angle"] = [2 * pi]  # 100%
        df["color"] = ["#d9d9d9"]
    else:
        if num_products <= 20:
            palette = Category20c[num_products]
        else:
            palette = Category20c[20]
        df["color"] = palette[:num_products]
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
    }

    return render(request, "pages/sales_chart.html", content)
