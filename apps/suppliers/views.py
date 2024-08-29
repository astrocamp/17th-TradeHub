# Create your views here.
from django.shortcuts import get_object_or_404, redirect, render

from .forms.form import SupplierForm
from .models import Supplier

from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")
