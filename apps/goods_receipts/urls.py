from django.urls import path

from . import views

app_name = "goods_receipts"

urlpatterns = [
    path("", views.index, name="GRindex"),
    path("new", views.new, name="GRnew"),
    path("<int:id>", views.show, name="GRshow"),
    path("edit/<int:id>", views.edit, name="GRedit"),
    path("delete/<int:id>", views.delete, name="GRdelete"),
]
