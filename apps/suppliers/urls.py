from django.urls import path

from . import views
from .views import DataListView

app_name = "suppliers"

urlpatterns = [
    path("", DataListView.as_view(), name="index"),
    path("new", views.new, name="new"),
    path("delete/many", views.delete_selected_suppliers, name="delete_selected"),
    path("show/<int:id>", views.show, name="show"),
    path("edit/<int:id>", views.edit, name="edit"),
    path("delete/<int:id>", views.delete, name="delete"),
]
