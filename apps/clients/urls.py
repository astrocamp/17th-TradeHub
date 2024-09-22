from django.urls import path

from . import views

app_name = "clients"

urlpatterns = [
    path("", views.index, name="index"),
    path("new", views.new, name="new"),
    path("edit/<int:id>", views.client_update_and_delete, name="edit"),
    path("import", views.import_file, name="import_file"),
    path("export_excel", views.export_excel, name="export_excel"),
    path("export_sample", views.export_sample, name="export_sample"),
]
