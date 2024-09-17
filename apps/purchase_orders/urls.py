from django.urls import path

from apps.purchase_orders import views

app_name = "purchase_orders"

urlpatterns = [
    path("", views.index, name="index"),
    path("new", views.new, name="new"),
    path("delete/many", views.delete_selected_purchase_orders, name="delete_selected"),
    path("show/<int:id>", views.show, name="show"),
    path("edit/<int:id>", views.edit, name="edit"),
    path("delete/<int:id>", views.delete, name="delete"),
    path("load_supplier_info/", views.load_supplier_info, name="load_supplier_info"),
    path("import", views.import_file, name="import_file"),
    path("export_csv", views.export_csv, name="export_csv"),
    path("export_excel", views.export_excel, name="export_excel"),
]
