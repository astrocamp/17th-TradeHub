from debug_toolbar.toolbar import debug_toolbar_urls
from django.urls import path

from . import views

app_name = "clients"

urlpatterns = [
    path("index", views.index, name="index"),
    path("new", views.new, name="new"),
    path("index", views.index, name="index"),
    path("edit/<int:id>", views.client_update_and_delete, name="edit"),
]
