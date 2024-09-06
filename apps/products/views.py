from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView

from .forms.product_form import ProductForm
from .models import Product


class DataListView(ListView):
    model = Product
    template_name = "pages/index.html"
    context_object_name = "products"
    paginate_by = 5


def index(request):
    state = request.GET.get("select")
    order_by = request.GET.get("sort", "id")
    is_desc = request.GET.get("desc", True) == "False"
    state_match = {"often", "haply", "never"}

    products = Product.objects.all()

    if state in state_match:
        products = Product.objects.filter(state=state)
    order_by_field = f"{'-' if is_desc else ''}{order_by}"
    products = products.order_by(order_by_field)

    content = {
        "products": products,
        "selected_state": state,
        "order_by": order_by,
        "is_desc": is_desc,
    }

    return render(request, "pages/index.html", content)


def new(request):
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("products:index")
        return render(request, "pages/new.html", {"form": form})
    form = ProductForm()
    return render(request, "pages/new.html", {"form": form})


def edit(request, id):
    if request.method == "POST":
        product = get_object_or_404(Product, id=id)
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect("products:index")
        return render(request, "pages/edit.html", {"product": product, "form": form})
    product = get_object_or_404(Product, id=id)
    form = ProductForm(instance=product)
    return render(request, "pages/edit.html", {"product": product, "form": form})


def delete(request, id):
    product = get_object_or_404(Product, id=id)
    product.delete()
    return redirect("products:index")
