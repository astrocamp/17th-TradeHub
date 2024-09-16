from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms.product_form import ProductForm
from .models import Product


def index(request):
    state = request.GET.get("select")
    order_by = request.GET.get("sort", "id")
    is_desc = request.GET.get("desc", True) == "False"
    state_match = {"often", "haply", "never"}

    products = Product.objects.all()

    if state in state_match:
        products = Product.objects.filter(state=state)
    order_by_field = order_by if is_desc else "-" + order_by
    products = products.order_by(order_by_field)

    paginator = Paginator(products, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    content = {
        "products": page_obj,
        "selected_state": state,
        "order_by": order_by,
        "is_desc": is_desc,
        "page_obj": page_obj,
    }

    return render(request, "products/index.html", content)


def new(request):
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("products:index")
        return render(request, "products/new.html", {"form": form})
    form = ProductForm()
    return render(request, "products/new.html", {"form": form})


def edit(request, id):
    product = get_object_or_404(Product, id=id)
    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect("products:index")

    else:
        form = ProductForm(instance=product)
    return render(request, "products/edit.html", {"product": product, "form": form})


def delete(request, id):
    product = get_object_or_404(Product, id=id)
    product.delete()
    messages.success(request, "刪除完成!")
    return redirect("products:index")
