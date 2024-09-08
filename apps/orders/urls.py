from debug_toolbar.toolbar import debug_toolbar_urls
from django.urls import include, path

from . import views

app_name = "orders"

urlpatterns = [
    path("", views.index, name="index"),
    path("create", views.new, name="create"),
    path("edit/<int:id>", views.order_update_and_delete, name="edit"),
]
