from django.contrib import messages
from django.core.paginator import Paginator
from django.forms import inlineformset_factory
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.suppliers.models import Supplier

from .forms.purchase_orders_form import (ProductItemForm, ProductItemFormSet,
                                         PurchaseOrderForm)
from .models import ProductItem, PurchaseOrder


def index(request):
    state = request.GET.get("select")
    order_by = request.GET.get("sort", "id")
    is_desc = request.GET.get("desc", "True") == "False"

    purchase_orders = PurchaseOrder.objects.all()

    if state in PurchaseOrder.AVAILABLE_STATES:
        purchase_orders = purchase_orders.filter(state=state)
    order_by_field = order_by if is_desc else "-" + order_by
    purchase_orders = purchase_orders.order_by(order_by_field)
    paginator = Paginator(purchase_orders, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    content = {
        "purchase_orders": page_obj,
        "selected_state": state,
        "order_by": order_by,
        "is_desc": is_desc,
        "page_obj": page_obj,
    }

    if request.method == "POST":
        form = PurchaseOrderForm(request.POST)
        formset = ProductItemFormSet(request.POST, instance=form.instance)
        if form.is_valid() and formset.is_valid():
            order = form.save()
            formset.instance = order
            formset.save()
            return redirect("purchase_orders:index")
        else:
            return render(
                request, "purchase_orders/new.html", {"form": form, "formset": formset}
            )

    purchase_orders = PurchaseOrder.objects.order_by("id")
    return render(
        request, "purchase_orders/index.html", {"purchase_orders": purchase_orders}
    )


from django.utils import timezone

from .models import PurchaseOrder


def new(request):
    today = timezone.localtime().strftime("%Y%m%d")
    last_order = (
        PurchaseOrder.objects.filter(order_number__startswith=today)
        .order_by("-order_number")
        .first()
    )
    if last_order:
        last_order_number = int(last_order.order_number[-3:])
        new_order_number = f"{today}{last_order_number + 1:03d}"
    else:
        new_order_number = f"{today}001"

    form = PurchaseOrderForm(initial={"order_number": new_order_number})
    formset = ProductItemFormSet(instance=form.instance)
    return render(
        request,
        "purchase_orders/new.html",
        {"form": form, "formset": formset},
    )


def show(request, id):
    purchase_order = get_object_or_404(PurchaseOrder, id=id)
    if request.method == "POST":
        form = PurchaseOrderForm(request.POST, instance=purchase_order)
        formset = ProductItemFormSet(request.POST, instance=purchase_order)

        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect("purchase_orders:show", purchase_order.id)

        else:
            return render(
                request,
                "purchase_orders/edit.html",
                {"form": form, "formset": formset, "purchase_order": purchase_order},
            )

    product_items = ProductItem.objects.filter(purchase_order=purchase_order)
    return render(
        request,
        "purchase_orders/show.html",
        {"purchase_order": purchase_order, "product_items": product_items},
    )


def edit(request, id):
    purchase_order = get_object_or_404(PurchaseOrder, id=id)
    form = PurchaseOrderForm(instance=purchase_order)
    formset = get_product_item_formset(0)(instance=purchase_order)
    return render(
        request,
        "purchase_orders/edit.html",
        {"form": form, "formset": formset, "purchase_order": purchase_order},
    )


def get_product_item_formset(extra):
    return inlineformset_factory(
        PurchaseOrder,
        ProductItem,
        form=ProductItemForm,
        extra=extra,
        can_delete=True,
    )


def delete(request, id):
    purchase_order = get_object_or_404(PurchaseOrder, pk=id)
    purchase_order.delete()
    messages.success(request, "刪除完成!")
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
