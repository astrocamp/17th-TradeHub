from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from apps.goods_receipts.models import GoodsReceipt

from .forms import GoodsReceiptForm


def index(request):
    if request.method == "POST":
        form = GoodsReceiptForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("goods_receipts:index")
        return render(request, "pages/GRnew.html", {"form": form})
    goods_receipts = GoodsReceipt.objects.order_by("-id")
    paginator = Paginator(goods_receipts, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    content = {
        "goods_receipts": page_obj,
        "page_obj": page_obj,
    }
    return render(request, "pages/GRindex.html", content)


def new(request):
    form = GoodsReceiptForm
    return render(request, "pages/GRnew.html", {"form": form})


def show(request, id):
    goods_receipt = get_object_or_404(GoodsReceipt, id=id)
    if request.method == "POST":
        form = GoodsReceiptForm(request.POST, instance=goods_receipt)
        if form.is_valid():
            form.save()
            return redirect("goods_receipts:index")
        return render(
            request, "pages/GRedit.html", {"goods_receipt": goods_receipt, "form": form}
        )
    return render(request, "pages/GRshow.html", {"goods_receipt": goods_receipt})


def edit(request, id):
    goods_receipt = get_object_or_404(GoodsReceipt, id=id)
    form = GoodsReceiptForm(instance=goods_receipt)
    return render(
        request, "pages/GRedit.html", {"goods_receipt": goods_receipt, "form": form}
    )


def delete(request, id):
    goods_receipt = get_object_or_404(GoodsReceipt, id=id)
    goods_receipt.delete()
    return redirect("goods_receipts:index")
