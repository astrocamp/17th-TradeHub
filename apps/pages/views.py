from django.shortcuts import render

from apps.clients.forms.clients_form import ClientForm
from apps.clients.models import Client
from apps.goods_receipts.forms.goods_receipts_form import GoodsReceiptForm
from apps.goods_receipts.models import GoodsReceipt
from apps.inventory.forms.inventory_form import RestockForm
from apps.inventory.models import Inventory
from apps.orders.forms.form import OrderForm
from apps.orders.models import Orders
from apps.products.forms import ProductForm
from apps.products.models import Product
from apps.purchase_orders.forms.purchase_orders_form import PurchaseOrderForm
from apps.purchase_orders.models import PurchaseOrder
from apps.sales_orders.forms.sales_order_form import SalesOrderForm
from apps.sales_orders.models import SalesOrder
from apps.suppliers.forms.form import SupplierForm
from apps.suppliers.models import Supplier


def home(request):
    return render(request, "pages/home.html")


def about(request):
    return render(request, "pages/about.html")


def search(request):
    search = request.POST.get("search", "")
    category = request.POST.get("select")

    if category == "Product":
        products = Product.objects.filter(product_name__contains=search)
        results = [fields[:-1] for fields in products.values_list()]
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
        orders = Orders.objects.filter(code__contains=search)
        results = []
        for order in orders:
            results += [
                (
                    order.id,
                    order.code,
                    order.client.name,
                    order.product.product_name,
                    order.price,
                    order.quantity,
                    order.stock_quantity.quantity,
                )
            ]
        fields_names = [fields for fields in OrderForm._meta.labels.values()]
    elif category == "PurchaseOrder":
        purchase = PurchaseOrder.objects.filter(order_number__contains=search)
        results = []
        for order in purchase:
            results += [
                (
                    order.order_number,
                    order.supplier.name,
                    order.supplier_tel,
                    order.amount,
                    order.note,
                    order.updated_at,
                )
            ]
        fields_names = [fields for fields in PurchaseOrderForm._meta.labels.values()]
    elif category == "SalesOrder":
        purchase = SalesOrder.objects.filter(product__product_name__contains=search)
        results = []
        for order in purchase:
            results += [
                (
                    item.client,
                    item.product,
                    item.quantity,
                    item.stock,
                    item.price,
                    item.last_updated,
                    item.note,
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
                    order.amount,
                    order.note,
                    order.updated_at,
                )
            ]
        fields_names = [fields for fields in GoodsReceiptForm._meta.labels.values()]

    print(results)
    # print([result for result in results])

    content = {
        "search": search,
        "category": category,
        "results": results,
        "fields_names": fields_names,
    }
    return render(request, "pages/results.html", content)
