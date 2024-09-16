import csv

import pandas as pd
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from apps.goods_receipts.models import GoodsReceipt
from apps.products.models import Product
from apps.suppliers.models import Supplier

from .forms.goods_receipt_form import FileUploadForm, GoodsReceiptForm


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


def import_file(request):
    if request.method == "POST":
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES["file"]
            if file.name.endswith(".csv"):

                decoded_file = file.read().decode("utf-8").splitlines()
                reader = csv.reader(decoded_file)
                next(reader)  # Skip header row

                for row in reader:
                    if len(row) < 6:
                        messages.error(request, f"CSV 数据不完整，跳过该行: {row}")
                        continue
                    try:
                        supplier = Supplier.objects.get(id=row[1])
                        goods_name = Product.objects.get(id=row[2])
                        GoodsReceipt.objects.create(
                            receipt_number=row[0],
                            supplier=supplier,
                            goods_name=goods_name,
                            quantity=row[3],
                            method=row[4],
                            note=row[5],
                        )
                    except (Supplier.DoesNotExist, Product.DoesNotExist) as e:
                        messages.error(request, f"匯入失敗，找不到客戶或產品: {e}")
                        return redirect("goods_receipts:index")

                messages.success(request, "成功匯入 CSV")
                return redirect("goods_receipts:index")

            elif file.name.endswith(".xlsx"):
                df = pd.read_excel(file)
                df.rename(
                    columns={
                        "收據號碼": "receipt_number",
                        "供應商": "supplier",
                        "產品": "goods_name",
                        "數量": "quantity",
                        "傳送方式": "method",
                        "備註": "note",
                    },
                    inplace=True,
                )
                for _, row in df.iterrows():
                    try:
                        goods_name = Product.objects.get(id=int(row["goods_name"]))
                        supplier = Supplier.objects.get(id=int(row["supplier"]))
                        GoodsReceipt.objects.create(
                            receipt_number=str(row["receipt_number"]),
                            supplier=supplier,
                            goods_name=goods_name,
                            quantity=str(row["quantity"]),
                            method=str(row[4]),
                            note=str(row["note"]) if not pd.isna(row["note"]) else "",
                        )
                    except (Supplier.DoesNotExist, Product.DoesNotExist) as e:
                        messages.error(request, f"匯入失敗，找不到客戶或產品: {e}")
                        return redirect("goods_receipts:index")
                messages.success(request, "成功匯入 Excel")
                return redirect("goods_receipts:index")

            else:
                messages.error(request, "匯入失敗(檔案不是 CSV 或 Excel)")
                return render(request, "layouts/import.html", {"form": form})

    form = FileUploadForm()
    return render(request, "layouts/import.html", {"form": form})


def export_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="GoodsReceipts.csv"'

    writer = csv.writer(response)
    writer.writerow(
        [
            "收據號碼",
            "供應商",
            "產品",
            "數量",
            "傳送方式",
            "建立時間",
            "刪除時間",
            "備註",
        ]
    )

    goods_receipts = GoodsReceipt.objects.all()
    for goods_receipt in goods_receipts:
        writer.writerow(
            [
                goods_receipt.receipt_number,
                goods_receipt.supplier,
                goods_receipt.goods_name,
                goods_receipt.quantity,
                goods_receipt.method,
                goods_receipt.date,
                goods_receipt.deleted_at,
                goods_receipt.note,
            ]
        )

    return response


def export_excel(request):
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = "attachment; filename=GoodsReceipts.xlsx"

    goods_receipts = GoodsReceipt.objects.select_related("product", "supplier").values(
        "receipt_number",
        "supplier__name",
        "goods_name__product_name",
        "quantity",
        "method",
        "date",
        "deleted_at",
        "note",
    )

    df = pd.DataFrame(goods_receipts)
    for col in df.select_dtypes(include=["datetime64[ns, UTC]"]).columns:
        df[col] = df[col].dt.strftime("%Y-%m-%d")

    column_mapping = {
        "receipt_number": "收據號碼",
        "supplier__name": "供應商",
        "goods_name__product_name": "產品",
        "quantity": "數量",
        "method": "傳送方式",
        "date": "建立時間",
        "deleted_at": "刪除時間",
        "note": "備註",
    }

    df.rename(columns=column_mapping, inplace=True)

    with pd.ExcelWriter(response, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="GoodsReceipts")
    return response
