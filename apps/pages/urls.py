from django.urls import path

from . import views

app_name = "pages"


urlpatterns = [
    path("", views.sales_chart, name="home"),
    path("home", views.out_home, name="out_home"),
    path("search/", views.search, name="search"),
]
