from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms.purchase_orders_form import PurchaseOrderForm  # Update import
from .models import PurchaseOrder  # Update import


def index(request):
    if request.method == "POST":
        form = PurchaseOrderForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("purchase_orders:index")  # Update redirect URL
        else:
            return render(request, "purchase_orders/new.html", {"form": form})

    purchase_orders = PurchaseOrder.objects.order_by("id")  # Update model
    return render(
        request, "purchase_orders/index.html", {"purchase_orders": purchase_orders}
    )  # Update context


def new(request):
    form = PurchaseOrderForm()  # Update form
    return render(
        request, "purchase_orders/new.html", {"form": form}
    )  # Update template


def show(req, id):
    purchase_order = get_object_or_404(PurchaseOrder, pk=id)
    if req.method == "POST":
        form = PurchaseOrderForm(req.POST, instance=purchase_order)
        if form.is_valid():
            form.save()
            return redirect("purchase_orders:show", purchase_order.id)
        else:
            return render(
                req,
                "purchase_orders/edit.html",
                {"purchase_order": purchase_order, "form": form},
            )
    return render(req, "purchase_orders/show.html", {"purchase_order": purchase_order})


def edit(req, id):
    purchase_order = get_object_or_404(PurchaseOrder, pk=id)
    form = PurchaseOrderForm(instance=purchase_order)
    return render(
        req,
        "purchase_orders/edit.html",
        {"purchase_order": purchase_order, "form": form},
    )


@require_POST
def delete_selected_purchase_orders(request):
    selected_purchase_orders = request.POST.getlist("selected_purchase_orders")
    PurchaseOrder.objects.filter(id__in=selected_purchase_orders).delete()
    return redirect("purchase_orders:index")  # Update redirect URL
