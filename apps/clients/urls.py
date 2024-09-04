from debug_toolbar.toolbar import debug_toolbar_urls
from django.urls import path

from . import views
from .views import DataListView

app_name = "clients"

urlpatterns = [
    path("", DataListView.as_view(), name="list"),
    path("index", views.index, name="index"),
    path("create", views.create, name="create"),
    path("edit/<int:id>", views.client_update_and_delete, name="edit"),
] + debug_toolbar_urls()
