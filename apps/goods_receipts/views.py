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

    content = {
        "goods_receipts": goods_receipts,
        "selected_state": state,
        "is_desc": is_desc,
        "order_by": order_by,
    }
    if req.method == "POST":
        form = GoodsReceiptForm(req.POST)
        if form.is_valid():
            form.save()
            return redirect("goods_receipts:GRindex")
        return render(req, "pages/GRnew.html", {"form": form})
    return render(req, "pages/GRindex.html", content)


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
