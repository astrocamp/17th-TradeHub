from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView

from apps.goods_receipts.models import GoodsReceipt

from .forms import GoodsReceiptForm


class DataListView(ListView):
    model = GoodsReceipt
    template_name = "pages/GRindex.html"
    context_object_name = "goods_receipts"
    paginate_by = 5


def index(req):
    if req.method == "POST":
        form = GoodsReceiptForm(req.POST)
        if form.is_valid():
            form.save()
            return redirect("goods_receipts:GRindex")
        return render(req, "pages/GRnew.html", {"form": form})
    goods_receipts = GoodsReceipt.objects.order_by("-id")
    return goods_receipts


def new(req):
    form = GoodsReceiptForm
    return render(req, "pages/GRnew.html", {"form": form})


def show(req, id):
    goods_receipt = get_object_or_404(GoodsReceipt, id=id)
    if req.method == "POST":
        form = GoodsReceiptForm(req.POST, instance=goods_receipt)
        if form.is_valid():
            form.save()
            return redirect("goods_receipts:GRshow", id=id)
        return render(
            req, "pages/GRedit.html", {"goods_receipt": goods_receipt, "form": form}
        )
    return render(req, "pages/GRshow.html", {"goods_receipt": goods_receipt})


def edit(req, id):
    goods_receipt = get_object_or_404(GoodsReceipt, id=id)
    form = GoodsReceiptForm(instance=goods_receipt)
    return render(
        req, "pages/GRedit.html", {"goods_receipt": goods_receipt, "form": form}
    )


def delete(req, id):
    goods_receipt = get_object_or_404(GoodsReceipt, id=id)
    goods_receipt.delete()
    return redirect("goods_receipts:GRindex")
