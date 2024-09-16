from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms.form import OrderForm
from .models import Orders


def index(request):
    state = request.GET.get("select")
    order_by = request.GET.get("sort", "id")
    is_desc = request.GET.get("desc", "True") == "False"

    orders = Orders.objects.all()

    if state in Orders.AVAILABLE_STATES:
        orders = Orders.objects.filter(state=state)
    order_by_field = order_by if is_desc else "-" + order_by
    orders = orders.order_by(order_by_field)

    paginator = Paginator(orders, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    content = {
        "state": state,
        "order_by": order_by,
        "is_desc": is_desc,
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
    return render(request, "orders/new.html", {"form": form})


def order_update_and_delete(request, id):
    order = get_object_or_404(Orders, id=id)
    if request.method == "POST":
        if "delete" in request.POST:
            order.delete()
            messages.success(request, "刪除完成!")
            return redirect("orders:index")
        else:
            form = OrderForm(request.POST, instance=order)
            if form.is_valid():
                form.save()
                return redirect("orders:index")
    form = OrderForm(instance=order)
    return render(request, "orders/edit.html", {"order": order, "form": form})
