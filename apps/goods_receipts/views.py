from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from apps.goods_receipts.models import GoodsReceipt

from .forms import GoodsReceiptForm


def index(req):
    state = req.GET.get("select")
    order_by = req.GET.get("sort", "id")
    is_desc = req.GET.get("desc", "True") == "False"

    goods_receipts = GoodsReceipt.objects.all()

    if state in GoodsReceipt.AVAILABLE_STATES:
        goods_receipts = GoodsReceipt.objects.filter(state=state)
    order_by_field = order_by if is_desc else "-" + order_by
    goods_receipts = goods_receipts.order_by(order_by_field)
    paginator = Paginator(goods_receipts, 5)
    page_number = req.GET.get("page")
    page_obj = paginator.get_page(page_number)

    content = {
        "goods_receipts": page_obj,
        "selected_state": state,
        "is_desc": is_desc,
        "order_by": order_by,
        "page_obj": page_obj,
    }
    if req.method == "POST":
        form = GoodsReceiptForm(req.POST)
        if form.is_valid():
            form.save()
            return redirect("goods_receipts:index")
        return render(req, "goods_receipts/new.html", {"form": form})
    return render(req, "goods_receipts/index.html", content)


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
    return redirect("goods_receipts:index")
