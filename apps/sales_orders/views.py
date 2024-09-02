from django.shortcuts import get_object_or_404, redirect, render

from .forms.sales_order_form import SalesOrderForm
from .models import SalesOrder


def index(request):
    state = request.GET.get("select")
    order_by = request.GET.get("sort", "id")
    is_desc = request.GET.get("desc", "True") == "False"
    state_match = {"finish", "unfinish"}

    sales_order = SalesOrder.objects.order_by(order_by)

    if state in state_match:
        sales_order = SalesOrder.objects.filter(state=state)
    order_by_field = f"{'-' if is_desc else ''}{order_by}"
    sales_order = sales_order.order_by(order_by_field)

    content = {
        "sales_order": sales_order,
        "selected_state": state,
        "is_desc": is_desc,
        "order_by": order_by,
    }

    return render(request, "pages/order_index.html", content)


def create(request):
    if request.method == "POST":
        form = SalesOrderForm(request.POST)
        if form.is_valid():
            form.save().update_state()
            return redirect("sales_orders:index")
    form = SalesOrderForm()
    return render(request, "pages/order_create.html", {"form": form})


def edit(request, id):
    sales_order = get_object_or_404(SalesOrder, id=id)
    if request.method == "POST":
        form = SalesOrderForm(request.POST, instance=sales_order)
        if form.is_valid():
            form.save().update_state()
            return redirect("sales_orders:index")
    else:
        form = SalesOrderForm(instance=sales_order)

    return render(
        request,
        "pages/order_edit.html",
        {"sales_order": sales_order, "form": form},
    )


def delete(request, id):
    sales_order = get_object_or_404(SalesOrder, id=id)
    sales_order.delete()
    return redirect("orders:index")
