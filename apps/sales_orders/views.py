from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms.sales_order_form import SalesOrderForm
from .models import SalesOrder


def index(request):
    state = request.GET.get("select")
    order_by = request.GET.get("sort", "id")
    is_desc = request.GET.get("desc", "True") == "False"

    sales_orders = SalesOrder.objects.all()

    if state in SalesOrder.AVAILABLE_STATES:
        sales_orders = SalesOrder.objects.filter(state=state)
    order_by_field = order_by if is_desc else "-" + order_by
    sales_orders = sales_orders.order_by(order_by_field)
    paginator = Paginator(sales_orders, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    content = {
        "sales_orders": page_obj,
        "selected_state": state,
        "is_desc": is_desc,
        "order_by": order_by,
        "page_obj": page_obj,
    }

    return render(request, "pages/order_index.html", content)


def create(request):
    if request.method == "POST":
        form = SalesOrderForm(request.POST)
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
