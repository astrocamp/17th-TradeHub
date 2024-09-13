from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms.form import SupplierForm
from .models import Supplier


def index(request):
    state = request.GET.get("select")
    order_by = request.GET.get("sort", "id")
    is_desc = request.GET.get("desc", "True") == "False"
    state_match = {"often", "haply", "never"}

    suppliers = Supplier.objects.all()

    if state in state_match:
        suppliers = Supplier.objects.filter(state=state)
    order_by_field = order_by if is_desc else "-" + order_by
    suppliers = suppliers.order_by(order_by_field)
    paginator = Paginator(suppliers, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    content = {
        "suppliers": page_obj,
        "selected_state": state,
        "order_by": order_by,
        "is_desc": is_desc,
        "page_obj": page_obj,
    }
    if request.method == "POST":
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("suppliers:index")
        else:
            return render(request, "suppliers/new.html", {"form": form})

    # suppliers = Supplier.objects.order_by("id")
    paginator = Paginator(suppliers, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    content = {
        "suppliers": suppliers,
        "selected_state": state,
        "order_by": order_by,
        "is_desc": is_desc,
        "suppliers": page_obj,
        "page_obj": page_obj,
    }

    return render(request, "suppliers/index.html", content)


def new(request):
    form = SupplierForm()
    return render(request, "suppliers/new.html", {"form": form})


def show(req, id):
    supplier = get_object_or_404(Supplier, pk=id)
    if req.method == "POST":
        form = SupplierForm(req.POST, instance=supplier)
        if form.is_valid():
            form.save()
            return redirect("suppliers:index")
        else:
            return render(
                req, "suppliers/edit.html", {"supplier": supplier, "form": form}
            )
    return render(req, "suppliers/show.html", {"supplier": supplier})


def edit(req, id):
    supplier = get_object_or_404(Supplier, pk=id)
    form = SupplierForm(instance=supplier)
    return render(req, "suppliers/edit.html", {"supplier": supplier, "form": form})


def delete(req, id):
    supplier = get_object_or_404(Supplier, pk=id)
    supplier.delete()
    return redirect("suppliers:index")


@require_POST
def delete_selected_suppliers(request):
    selected_suppliers = request.POST.getlist("selected_suppliers")
    Supplier.objects.filter(id__in=selected_suppliers).delete()
    return redirect("suppliers:index")
