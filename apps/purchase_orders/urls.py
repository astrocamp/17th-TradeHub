from django.urls import path
from . import views

app_name = 'purchase_orders'

urlpatterns = [
    path('', views.index, name='index'),
]
