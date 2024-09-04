from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView

from .forms.sales_order_form import SalesOrderForm
from .models import SalesOrder


class DataListView(ListView):
    model = SalesOrder
    template_name = "pages/order_index.html"
    context_object_name = "sales_orders"
    paginate_by = 5


def index(request):
    state = request.GET.get("select")
    order_by = request.GET.get("sort", "id")
    is_desc = request.GET.get("desc", "True") == "False"
    state_match = {"finish", "unfinish"}

    sales_orders = SalesOrder.objects.order_by(order_by)

    if state in state_match:
        sales_orders = SalesOrder.objects.filter(state=state)
    order_by_field = f"{'-' if is_desc else ''}{order_by}"
    sales_orders = sales_orders.order_by(order_by_field)

    content = {
        "sales_orders": sales_orders,
        "selected_state": state,
        "is_desc": is_desc,
        "order_by": order_by,
    }

    return render(request, "pages/order_index.html", content)


def create(request):
    if request.method == "POST":
        form = SalesOrderForm(request.POST)
        print(form.is_valid())
        print(form.errors)
        if form.is_valid():
            form.save()
            return redirect("sales_orders:index")
    else:
        form = SalesOrderForm()
    return render(request, "pages/order_create.html", {"form": form})


def edit(request, id):
    sales_orders = get_object_or_404(SalesOrder, id=id)
    if request.method == "POST":
        form = SalesOrderForm(request.POST, instance=sales_orders)
        if form.is_valid():
            form.save()
            return redirect("sales_orders:index")
    else:
        form = SalesOrderForm(instance=sales_orders)

    return render(
        request,
        "pages/order_edit.html",
        {"sales_orders": sales_orders, "form": form},
    )


def delete(request, id):
    sales_orders = get_object_or_404(SalesOrder, id=id)
    sales_orders.delete()
    return redirect("sales_orders:index")
