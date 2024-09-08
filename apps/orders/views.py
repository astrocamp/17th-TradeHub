from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms.form import OrderForm
from .models import Orders


def index(request):
    orders = Orders.objects.order_by("id")
    paginator = Paginator(orders, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    content = {
        "orders": page_obj,
        "page_obj": page_obj,
    }

    return render(request, "orders/orders_list.html", content)


def new(request):
    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("orders:index")
    form = OrderForm()
    return render(request, "orders/orders_create.html", {"form": form})


def order_update_and_delete(request, id):
    order = get_object_or_404(Orders, id=id)
    if request.method == "POST":
        if "delete" in request.POST:
            order.delete()
            return redirect("orders:index")
        else:
            form = OrderForm(request.POST, instance=order)
            if form.is_valid():
                form.save()
                return redirect("orders:index")
    form = OrderForm(instance=order)
    return render(request, "orders/orders_edit.html", {"order": order, "form": form})
