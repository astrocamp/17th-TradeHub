from django.shortcuts import get_object_or_404, redirect, render

from .forms.inventory_form import RestockForm
from .models import Inventory


def index(request):
    inventory = Inventory.objects.order_by("-id")
    return render(request, "pages/inventory_index.html", {"inventory": inventory})


def create(request):
    if request.method == "POST":
        form = RestockForm(request.POST)
        breakpoint()
        if form.is_valid():
            form.save()
            return redirect("inventory:create")
        return render(request, "pages/inventory_create.html", {"form": form})
    else:
        form = RestockForm()
        return render(request, "pages/inventory_create.html", {"form": form})


def edit(request, id):
    inventory = get_object_or_404(Inventory, id=id)
    if request.method == "POST":
        form = RestockForm(request.POST, instance=inventory)
        if form.is_valid():
            form.save()
            return redirect("inventory:index")
        return render(
            request, "pages/inventory_edit.html", {"inventory": inventory, "form": form}
        )
    else:
        form = RestockForm(instance=inventory)
        return render(
            request, "pages/inventory_edit.html", {"inventory": inventory, "form": form}
        )


def delete(request, id):
    inventory = get_object_or_404(Inventory, id=id)
    inventory.delete()
    return redirect("inventory:index")
