from debug_toolbar.toolbar import debug_toolbar_urls
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("", include("apps.pages.urls")),
    path("admin/", admin.site.urls),
    path("products/", include("apps.products.urls")),
    path("inventory/", include("apps.inventory.urls")),
    path("suppliers/", include("apps.suppliers.urls")),
    path("clients/", include("apps.clients.urls")),
    path("purchase-orders/", include("apps.purchase_orders.urls")),
    path("orders/", include("apps.orders.urls")),
    path("sales_orders/", include("apps.sales_orders.urls")),
    path("goods_receipts/", include("apps.goods_receipts.urls")),
] + debug_toolbar_urls()
