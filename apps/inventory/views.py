from datetime import datetime

from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView

from .forms.inventory_form import RestockForm
from .models import Inventory


class DataListView(ListView):
    model = Inventory
    template_name = "pages/inventory_index.html"
    context_object_name = "inventory"
    paginate_by = 5


def index(request):
    state = request.GET.get("select")
    order_by = request.GET.get("sort", "id")
    is_desc = request.GET.get("desc", "True") == "False"
    state_match = {"normal", "low_stock", "out_stock"}

    inventory = Inventory.objects.order_by(order_by)

    if state in state_match:
        inventory = Inventory.objects.filter(state=state)
    order_by_field = f"{'-' if is_desc else ''}{order_by}"
    inventory = inventory.order_by(order_by_field)

    content = {
        "inventory": inventory,
        "selected_state": state,
        "is_desc": is_desc,
        "order_by": order_by,
    }

    return render(request, "pages/inventory_index.html", content)


def create(request):
    if request.method == "POST":
        form = RestockForm(request.POST)
        if form.is_valid():
            form.save().update_state()
            return redirect("inventory:index")
    form = RestockForm()
    return render(request, "pages/inventory_create.html", {"form": form})


def edit(request, id):
    inventory = get_object_or_404(Inventory, id=id)
    if request.method == "POST":
        form = RestockForm(request.POST, instance=inventory)
        if form.is_valid():
            form.save().update_state()
            return redirect("inventory:index")
    else:
        form = RestockForm(instance=inventory)

    return render(
        request, "pages/inventory_edit.html", {"inventory": inventory, "form": form}
    )


def delete(request, id):
    inventory = get_object_or_404(Inventory, id=id)
    inventory.delete()
    return redirect("inventory:index")
