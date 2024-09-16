from datetime import datetime

from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms.inventory_form import RestockForm
from .models import Inventory


def index(request):
    state = request.GET.get("select")
    order_by = request.GET.get("sort", "id")
    is_desc = request.GET.get("desc", "True") == "False"
    state_match = {"normal", "low_stock", "out_stock"}

    inventory = Inventory.objects.order_by(order_by)

    if state in state_match:
        inventory = Inventory.objects.filter(state=state)
    order_by_field = order_by if is_desc else "-" + order_by
    inventory = inventory.order_by(order_by_field)

    paginator = Paginator(inventory, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    content = {
        "inventory": page_obj,
        "selected_state": state,
        "is_desc": is_desc,
        "order_by": order_by,
        "page_obj": page_obj,
    }

    return render(request, "inventory/index.html", content)


def new(request):
    if request.method == "POST":
        form = RestockForm(request.POST)
        if form.is_valid():
            form.save().update_state()
            return redirect("inventory:index")
        else:
            return render(request, "inventory/new.html", {"form": form})
    form = RestockForm()
    return render(request, "inventory/new.html", {"form": form})


def edit(request, id):
    inventory = get_object_or_404(Inventory, id=id)
    if request.method == "POST":
        form = RestockForm(request.POST, instance=inventory)
        print(form.errors)
        if form.is_valid():
            form.save().update_state()
            return redirect("inventory:index")
        else:
            print(form.errors)
    else:
        form = RestockForm(instance=inventory)

    return render(
        request, "inventory/edit.html", {"inventory": inventory, "form": form}
    )


def delete(request, id):
    inventory = get_object_or_404(Inventory, id=id)
    inventory.delete()
    messages.success(request, "刪除完成!")
    return redirect("inventory:index")
