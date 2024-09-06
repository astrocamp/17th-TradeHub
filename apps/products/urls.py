from django.urls import path

from . import views

app_name = "products"

urlpatterns = [
    path("", views.DataListView.as_view(), name="index"),
    path("new", views.new, name="new"),
    path("edit/<int:id>", views.edit, name="edit"),
    path("delete/<int:id>", views.delete, name="delete"),
]
