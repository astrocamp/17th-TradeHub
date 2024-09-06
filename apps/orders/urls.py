from debug_toolbar.toolbar import debug_toolbar_urls
from django.urls import include, path

from . import views

app_name = "orders"

urlpatterns = [
    path("", views.DataListView.as_view(), name="list"),
    path("create", views.create, name="create"),
    path("edit/<int:id>", views.order_update_and_delete, name="edit"),
]
