from django.urls import path

from . import views

app_name = "purchase_orders"

urlpatterns = [
    path("", views.index, name="index"),
    path("new", views.new, name="new"),
    path("delete/many", views.delete_selected_purchase_orders, name="delete_selected"),
    path("show/<int:id>", views.show, name="show"),
]
