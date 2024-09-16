from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import F
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.shortcuts import get_object_or_404, redirect, render

from apps.goods_receipts.models import GoodsReceipt
from apps.inventory.models import Inventory

from .forms import GoodsReceiptForm


def index(request):
    state = request.GET.get("select")
    order_by = request.GET.get("sort", "id")
    is_desc = request.GET.get("desc", "True") == "False"

    goods_receipts = GoodsReceipt.objects.all()

    if state in GoodsReceipt.AVAILABLE_STATES:
        goods_receipts = GoodsReceipt.objects.filter(state=state)
    order_by_field = order_by if is_desc else "-" + order_by
    goods_receipts = goods_receipts.order_by(order_by_field)
    paginator = Paginator(goods_receipts, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    content = {
        "goods_receipts": page_obj,
        "selected_state": state,
        "is_desc": is_desc,
        "order_by": order_by,
        "page_obj": page_obj,
    }
    if request.method == "POST":
        form = GoodsReceiptForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("goods_receipts:index")
        return render(request, "goods_receipts/new.html", {"form": form})
    return render(request, "goods_receipts/index.html", content)


def new(request):
    if request.method == "POST":
        form = GoodsReceiptForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("goods_receipts:index")
        return render(request, "goods_receipts/new.html", {"form": form})
    form = GoodsReceiptForm()
    return render(request, "goods_receipts/new.html", {"form": form})


def show(request, id):
    goods_receipt = get_object_or_404(GoodsReceipt, id=id)
    if request.method == "POST":
        form = GoodsReceiptForm(request.POST, instance=goods_receipt)
        if form.is_valid():
            form.save()
            return redirect("goods_receipts:index")
        return render(
            request,
            "goods_receipts/edit.html",
            {"goods_receipt": goods_receipt, "form": form},
        )
    return render(request, "goods_receipts/show.html", {"goods_receipt": goods_receipt})


def edit(request, id):
    if request.method == "POST":
        goods_receipt = get_object_or_404(GoodsReceipt, id=id)
        form = GoodsReceiptForm(request.POST, instance=goods_receipt)
        if form.is_valid():
            form.save()
            return redirect("goods_receipts:index")
        return render(
            request,
            "goods_receipts/edit.html",
            {"goods_receipt": goods_receipt, "form": form},
        )
    goods_receipt = get_object_or_404(GoodsReceipt, id=id)
    form = GoodsReceiptForm(instance=goods_receipt)
    return render(
        request,
        "goods_receipts/edit.html",
        {"goods_receipt": goods_receipt, "form": form},
    )


def delete(request, id):
    goods_receipt = get_object_or_404(GoodsReceipt, id=id)
    goods_receipt.delete()
    messages.success(request, "刪除完成!")
    return redirect("goods_receipts:index")


@receiver(pre_save, sender=GoodsReceipt)
def update_purchase_order_state(sender, instance, **kwargs):
    if instance.state == "TO_BE_STOCKED":
        Inventory.objects.filter(product=instance.goods_name).update(
            quantity=F("quantity") + instance.quantity
        )
        instance.set_finished()
