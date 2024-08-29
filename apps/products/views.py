from django.shortcuts import get_object_or_404, redirect, render

from .forms.product_form import ProductForm
from .models import Product


def index(req):
    if req.method == "POST":
        form = ProductForm(req.POST)
        if form.is_valid():
            form.save()
            return redirect("products:index")
        return render(req, "pages/new.html", {"form": form})

    products = Product.objects.order_by("-id")
    return render(req, "pages/index.html", {"products": products})


def new(req):
    form = ProductForm()
    return render(req, "pages/new.html", {"form": form})


def show(req, id):
    product = get_object_or_404(Product, id=id)
    if req.method == "POST":
        form = ProductForm(req.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect("products:show", id=id)
        return render(req, "pages/edit.html", {"product": product, "form": form})
    return render(req, "pages/show.html", {"product": product})


def edit(req, id):
    product = get_object_or_404(Product, id=id)
    form = ProductForm(instance=product)
    return render(req, "pages/edit.html", {"product": product, "form": form})


def delete(req, id):
    product = get_object_or_404(Product, id=id)
    product.delete()
    return redirect("products:index")
