from datetime import datetime

from django.shortcuts import get_object_or_404, redirect, render

from .models import Inventory

# from .form.form_inventory import InventoryForm


def index(request):
    inventory = Inventory.objects.order_by("-id")
    return render(request, "pages/index.html", {"inventory": inventory})


def edit(request, id):
    inventory = get_object_or_404(Inventory, id=id)
    if request.method == "POST":
        inventory.product = request.POST["product"]
        inventory.supplier = request.POST["supplier"]
        inventory.quantity = request.POST["quantity"]
        inventory.last_updated = datetime.now()
        inventory.save()
        return redirect("inventory:index")
    return render(request, "pages/index.html", {"inventory": inventory, "id": id})


def delete(request, id):
    inventory = get_object_or_404(Inventory, id=id)
    inventory.delete()
    return redirect("inventory:index")
