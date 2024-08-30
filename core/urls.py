from debug_toolbar.toolbar import debug_toolbar_urls
from django.contrib import admin
from django.urls import include, path

<<<<<<< HEAD

urlpatterns = [
    path("client/", include("apps.client.urls")),
    path("products", include("apps.products.urls")),
=======


urlpatterns = [
    path("", include("apps.pages.urls")),
>>>>>>> 364e2f2 (Create Inventory model and startapp pages and add base.html)
    path("admin/", admin.site.urls),
    path("inventory/", include("apps.inventory.urls")),
] + debug_toolbar_urls()
