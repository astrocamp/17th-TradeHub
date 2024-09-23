from django.urls import path

from . import views

app_name = "pages"


urlpatterns = [
    path("welcome/", views.welcome, name="welcome"),
    path("", views.sales_chart, name="home"),
    path("welcome/", views.welcome, name="welcome"),
    path("home", views.out_home, name="out_home"),
    path("search/", views.search, name="search"),
]
