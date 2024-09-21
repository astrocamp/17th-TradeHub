from django.urls import path

from . import views

app_name = "orders"

urlpatterns = [
    path("", views.index, name="index"),
    path("new", views.new, name="new"),
    path("edit/<int:id>", views.order_update_and_delete, name="edit"),
    path("transform/<int:id>", views.transform_sales_order, name="transform"),
    path("import", views.import_file, name="import_file"),
    path("export_csv", views.export_csv, name="export_csv"),
    path("export_excel", views.export_excel, name="export_excel"),
]
