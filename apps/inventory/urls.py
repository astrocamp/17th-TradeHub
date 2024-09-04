from django.urls import path

from . import views
from .views import DataListView

app_name = "inventory"


urlpatterns = [
    path("", DataListView.as_view(), name="index"),
    path("create", views.create, name="create"),
    path("edit/<int:id>", views.edit, name="edit"),
    path("delete/<int:id>", views.delete, name="delete"),
]
