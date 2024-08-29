from datetime import datetime

from django.shortcuts import redirect, render

from .models import Inventory


def index(request):
    inventory = Inventory.objects.order_by("-id")
    return render(request, "pages/index.html", {"inventory": inventory})


def edit(request, id):
    inventory = Inventory.objects.get(id=id)
    if request.method == "POST":
        inventory.product = request.POST["product"]
        inventory.supplier = request.POST["supplier"]
        inventory.quantity = request.POST["quantity"]
        inventory.last_updated = datetime.now()
        inventory.save()
        return redirect("inventory:index")
    return render(request, "pages/edit.html", {"inventory": inventory})


def delete(request, id):
    inventory = Inventory.objects.get(id=id)
    inventory.delete()
    return redirect("inventory:index")
