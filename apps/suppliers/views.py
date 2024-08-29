# Create your views here.
from django.shortcuts import get_object_or_404, redirect, render

from .forms.form import SupplierForm
from .models import Supplier


def index(req):
    if req.method == "POST":
        form = SupplierForm(req.POST)
        if form.is_valid():
            form.save()
            return redirect("suppliers:index")
        else:
            return render(req, "suppliers/new.html", {"form": form})
    suppliers = Supplier.objects.order_by("-id")
    return render(req, "suppliers/index.html", {"suppliers": suppliers})


def new(req):
    form = SupplierForm()
    return render(req, "suppliers/new.html", {"form": form})


def show(req, id):
    supplier = get_object_or_404(Supplier, pk=id)
    return render(req, "suppliers/show.html", {"supplier": supplier})
