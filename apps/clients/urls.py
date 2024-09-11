from debug_toolbar.toolbar import debug_toolbar_urls
from django.urls import include, path

from . import views

app_name = "clients"

urlpatterns = [
    path("", views.client_list, name="list"),
    path("index", views.index, name="index"),
    path("edit/<int:id>", views.client_update_and_delete, name="edit"),
] + debug_toolbar_urls()
