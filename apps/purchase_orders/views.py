from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.suppliers.models import Supplier

from .forms.purchase_orders_form import (PurchaseOrderForm,
                                         PurchaseOrderProductFormSet)
from .models import PurchaseOrder


def index(request):
    if request.method == "POST":
        form = PurchaseOrderForm(request.POST)
        formset = PurchaseOrderProductFormSet(request.POST, instance=form.instance)
        if form.is_valid() and formset.is_valid():
            purchase_order = form.save()
            formset.instance = purchase_order
            formset.save()
            return redirect("purchase_orders:index")
        else:
            form = PurchaseOrderForm()
            formset = PurchaseOrderProductFormSet(instance=form.instance)
            return render(
                request,
                "purchase_orders/new.html",
                {
                    "form": form,
                    "formset": formset,
                },
            )

    purchase_orders = PurchaseOrder.objects.order_by("id")
    return render(
        request, "purchase_orders/index.html", {"purchase_orders": purchase_orders}
    )


def new(request):
    form = PurchaseOrderForm()
    return render(request, "purchase_orders/new.html", {"form": form})


def show(request, id):
    purchase_order = get_object_or_404(PurchaseOrder, pk=id)
    if request.method == "POST":
        form = PurchaseOrderForm(request.POST, instance=purchase_order)
        if form.is_valid():
            form.save()
            return redirect("purchase_orders:show", purchase_order.id)
        else:
            return render(
                request,
                "purchase_orders/edit.html",
                {"purchase_order": purchase_order, "form": form},
            )
    return render(
        request, "purchase_orders/show.html", {"purchase_order": purchase_order}
    )


def edit(request, id):
    purchase_order = get_object_or_404(PurchaseOrder, pk=id)
    form = PurchaseOrderForm(instance=purchase_order)
    return render(
        request,
        "purchase_orders/edit.html",
        {"purchase_order": purchase_order, "form": form},
    )


@require_POST
def delete(request, id):
    purchase_order = get_object_or_404(PurchaseOrder, pk=id)
    purchase_order.delete()
    return redirect("purchase_orders:index")


@require_POST
def delete_selected_purchase_orders(request):
    selected_purchase_orders = request.POST.getlist("selected_purchase_orders")
    PurchaseOrder.objects.filter(id__in=selected_purchase_orders).delete()
    return redirect("purchase_orders:index")


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
    today = timezone.localtime().strftime("%Y%m%d")
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
