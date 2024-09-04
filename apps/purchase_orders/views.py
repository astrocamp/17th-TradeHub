from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.suppliers.models import Supplier

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


def delete(req, id):
    purchase_order = get_object_or_404(PurchaseOrder, pk=id)
    purchase_order.delete()
    return redirect("purchase_orders:index")


@require_POST
def delete_selected_purchase_orders(request):
    selected_purchase_orders = request.POST.getlist("selected_purchase_orders")
    PurchaseOrder.objects.filter(id__in=selected_purchase_orders).delete()
    return redirect("purchase_orders:index")  # Update redirect URL


def load_supplier_info(request):
    supplier_id = request.GET.get("supplier_id")
    supplier = Supplier.objects.get(id=supplier_id)
    data = {
        "supplier_tel": supplier.telephone,
        "contact_person": supplier.contact_person,
        "supplier_email": supplier.email,
    }
    return JsonResponse(data)


def generate_order_number(request):
    today = timezone.now().strftime("%Y%m%d")
    last_order = (
        PurchaseOrder.objects.filter(order_number__startswith=today)
        .order_by("order_number")
        .last()
    )

    if last_order:
        last_order_number = int(last_order.order_number[-3:])
        new_order_number = f"{last_order_number + 1:03d}"
    else:
        new_order_number = "001"

    order_number = f"{today}{new_order_number}"
    return JsonResponse({"order_number": order_number})
