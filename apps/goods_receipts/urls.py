from django.urls import path

from . import views
from .views import DataListView

app_name = "goods_receipts"

urlpatterns = [
    path("", DataListView.as_view(), name="GRindex"),
    path("new", views.new, name="GRnew"),
    path("<int:id>", views.show, name="GRshow"),
    path("edit/<int:id>", views.edit, name="GRedit"),
    path("delete/<int:id>", views.delete, name="GRdelete"),
]
