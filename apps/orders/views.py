from django.shortcuts import render, redirect, get_object_or_404
from .models import Orders


# Create your views here.
def order_list(req):
    orders = Orders.objects.order_by("-id")
    if req.method == "POST":
        order = Orders(
            code=req.POST["code"],
            client=req.POST["client"],
            product=req.POST["product"],
            note=req.POST["note"],
        )
        order.save()
        return redirect("orders:list")
    else:
        return render(req, "list.html", {"orders": orders})


def order_update_and_delete(req, id):
    order = get_object_or_404(Orders, id=id)
    if req.method == "POST":
        if "delete" in req.POST:
            order.delete()
            return redirect("orders:list")
        else:
            order.code = req.POST["code"]
            order.client = req.POST["client"]
            order.product = req.POST["product"]
            order.note = req.POST["note"]

            order.save()
            return redirect("order:list")

    return render(req, "edit.html", {"order": order})
