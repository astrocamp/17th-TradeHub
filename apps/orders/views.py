from django.shortcuts import get_object_or_404, redirect, render

from .forms.form import OrderForm
from .models import Orders


# Create your views here.
def order_list(req):
    orders = Orders.objects.order_by("-id")
    if req.method == "POST":
        form = OrderForm(req.POST)
        if form.is_valid():
            form.save()
            return redirect("orders:list")
    form = OrderForm()
    return render(req, "orders/orders_list.html", {"orders": orders, "form": form})


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
