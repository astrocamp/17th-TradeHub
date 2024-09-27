from django.urls import path

from . import views

app_name = "sales_orders"

urlpatterns = [
    path("", views.index, name="index"),
    path("new", views.new, name="new"),
    path("show/<int:id>", views.show, name="show"),
    path("edit/<int:id>/", views.edit, name="edit"),
    path("delete/<int:id>/", views.delete, name="delete"),
    path("load_client_info/", views.load_client_info, name="load_client_info"),
    path("load_product_info/", views.load_product_info, name="load_product_info"),
    path("export_excel", views.export_excel, name="export_excel"),
    path("transform/<int:id>", views.transform, name="transform"),
]
