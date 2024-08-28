from debug_toolbar.toolbar import debug_toolbar_urls
from django.urls import path, include
from . import views

app_name = "client"

urlpatterns = [
    path("", views.client_list, name="list"),
    path("edit/<int:id>", views.client_update_and_delete, name="edit"),
] + debug_toolbar_urls()
