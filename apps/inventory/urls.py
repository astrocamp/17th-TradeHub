from django.urls import path

from . import views

app_name = "inventory"


urlpatterns = [
    path("", views.index, name="index"),
    path("new", views.new, name="new"),
    path("show/<int:id>", views.show, name="show"),
    path("edit/<int:id>", views.edit, name="edit"),
    path("delete/<int:id>", views.delete, name="delete"),
    path("import", views.import_file, name="import_file"),
    path("export_excel", views.export_excel, name="export_excel"),
    path("export_sample", views.export_sample, name="export_sample"),
]
