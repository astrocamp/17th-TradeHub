from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView

from .forms.form import OrderForm
from .models import Orders


class DataListView(ListView):
    model = Orders
    template_name = "orders/orders_list.html"
    context_object_name = "orders"
    paginate_by = 5


def order_list(req):
    orders = Orders.objects.order_by("-id")
    return render(req, "orders/orders_list.html", {"orders": orders})


def create(request):
    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("orders:list")
    form = OrderForm()
    return render(request, "orders/orders_create.html", {"form": form})


def order_update_and_delete(req, id):
    order = get_object_or_404(Orders, id=id)
    if req.method == "POST":
        if "delete" in req.POST:
            order.delete()
            return redirect("orders:list")
        else:
            form = OrderForm(req.POST, instance=order)
            if form.is_valid():
                form.save()
                return redirect("orders:list")
    form = OrderForm(instance=order)
    return render(req, "orders/orders_edit.html", {"order": order, "form": form})
