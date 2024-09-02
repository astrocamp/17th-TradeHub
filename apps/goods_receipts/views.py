from django.shortcuts import render, get_object_or_404, redirect
from apps.goods_receipts.models import GoodsReceipt
from .forms import GoodsReceiptForm

# Create your views here.


def index(req):
    if req.method == "POST":
        form = GoodsReceiptForm(req.POST)
        if form.is_valid():
            form.save()
            return redirect("goods_receipts:GRindex")
        return render(req, "pages/GRnew.html", {"form":form})
    goods_receipts = GoodsReceipt.objects.order_by("-id")
    return render(req, "pages/GRindex.html", {"goods_receipts":goods_receipts})


def new(req):
    form = GoodsReceiptForm
    return render(req, "pages/GRnew.html", {"form":form})

def show(req, id):
    goods_receipt = get_object_or_404(GoodsReceipt, id=id)
    if req.method == "POST":
        form = GoodsReceiptForm(req.POST, instance=goods_receipt)
        if form.is_valid():
            form.save()
            return redirect("goods_receipts:GRshow", id=id)
        return render(req, "pages/GRedit.html", {"goods_receipt":goods_receipt, "form":form})
    return render(req, "pages/GRshow.html", {"goods_receipt":goods_receipt})

def edit(req, id):
    goods_receipt = get_object_or_404(GoodsReceipt, id=id)
    form = GoodsReceiptForm(instance=goods_receipt)
    return render(req, "pages/GRedit.html", {"goods_receipt":goods_receipt, "form":form})

def delete(req, id):
    goods_receipt = get_object_or_404(GoodsReceipt, id=id)
    goods_receipt.delete()
    return redirect("goods_receipts:GRindex")