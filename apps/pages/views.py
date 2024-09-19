import pandas as pd
from bokeh.embed import components
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure
from bokeh.resources import CDN
from django.db.models import Sum
from django.shortcuts import render

from apps.clients.models import Client
from apps.goods_receipts.models import GoodsReceipt
from apps.inventory.models import Inventory
from apps.orders.models import Orders
from apps.products.models import Product, Supplier
from apps.purchase_orders.models import PurchaseOrder
from apps.sales_orders.models import SalesOrder


def home(req):
    return render(req, "pages/home.html")


def about(req):
    return render(req, "pages/about.html")


def sales_chart(request):
    # 获取所有销售订单
    sales_orders = SalesOrder.objects.all()
    orders_num = len(Orders.objects.values("deleted_at").filter(deleted_at=None))
    sales_orders_num = len(
        SalesOrder.objects.values("deleted_at").filter(deleted_at=None)
    )
    purchase_orders_num = len(
        PurchaseOrder.objects.values("deleted_at").filter(deleted_at=None)
    )
    goods_receipts_num = len(
        GoodsReceipt.objects.values("deleted_at").filter(deleted_at=None)
    )
    clients_num = len(Client.objects.values("name"))
    products_num = len(Product.objects.values("product_number"))
    suppliers_num = len(Supplier.objects.values("name"))
    inventory_num = Inventory.objects.aggregate(total_quantity=Sum("quantity"))

    # 按产品汇总数量
    sales_data = (
        sales_orders.values("product__product_name")
        .annotate(total_quantity=Sum("quantity"))
        .order_by("-total_quantity")
    )

    # 转换为 DataFrame
    data = {
        "product": [item["product__product_name"] for item in sales_data],
        "quantity": [item["total_quantity"] for item in sales_data],
    }
    df = pd.DataFrame(data)

    # 为每个图表创建单独的数据源
    source1 = ColumnDataSource(df)
    source3 = ColumnDataSource(df)

    # 创建第一个图表
    p1 = figure(
        x_range=df["product"],
        title="Top Selling Products (Bar)",
        width=600,
        height=300,
        tools="pan,wheel_zoom,box_zoom,reset",
        toolbar_location="above",
    )
    p1.vbar(x="product", top="quantity", width=0.8, source=source1, color="blue")
    p1.xgrid.grid_line_color = None
    p1.y_range.start = 0
    p1.xaxis.major_label_orientation = "vertical"

    # 创建第三个图表 (折线图)
    p3 = figure(
        x_range=df["product"],
        title="Top Selling Products (Line)",
        sizing_mode="scale_width",
        height=500,
        tools="pan,wheel_zoom,box_zoom,reset",
        toolbar_location="above",
    )
    p3.line(x="product", y="quantity", line_width=2, source=source3, color="red")

    # 获取 Bokeh 图表组件和资源
    script1, div1 = components(p1)
    script3, div3 = components(p3)

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
        "script3": script3,
        "div3": div3,
        "bokeh_js": bokeh_js,
        "bokeh_css": bokeh_css,
    }

    # 将所有图表的组件和资源传递给模板
    return render(request, "pages/sales_chart.html", content)
