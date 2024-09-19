from django.urls import path

from . import views

app_name = "pages"


urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("sales-chart", views.sales_chart, name="sales_chart"),
]
