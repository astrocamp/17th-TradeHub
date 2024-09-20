import csv

import pandas as pd
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from apps.suppliers.models import Supplier

from .forms.product_form import FileUploadForm, ProductForm
from .models import Product


def index(request):
    state = request.GET.get("select")
    order_by = request.GET.get("sort", "id")
    is_desc = request.GET.get("desc", True) == "False"
    state_match = {"often", "haply", "never"}

    products = Product.objects.all()

    if state in state_match:
        products = Product.objects.filter(state=state)
    order_by_field = order_by if is_desc else "-" + order_by
    products = products.order_by(order_by_field)

    paginator = Paginator(products, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    content = {
        "products": page_obj,
        "selected_state": state,
        "order_by": order_by,
        "is_desc": is_desc,
        "page_obj": page_obj,
    }

    return render(request, "products/index.html", content)


def new(request):
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("products:index")
        return render(request, "products/new.html", {"form": form})
    form = ProductForm()
    return render(request, "products/new.html", {"form": form})


def edit(request, id):
    product = get_object_or_404(Product, id=id)
    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect("products:index")

    else:
        form = ProductForm(instance=product)
    return render(request, "products/edit.html", {"product": product, "form": form})


def delete(request, id):
    product = get_object_or_404(Product, id=id)
    product.delete()
    messages.success(request, "刪除完成!")
    return redirect("products:index")


def import_file(request):
    if request.method == "POST":
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES["file"]
            if file.name.endswith(".csv"):

                decoded_file = file.read().decode("utf-8").splitlines()
                reader = csv.reader(decoded_file)
                next(reader)

                for row in reader:
                    if len(row) < 1:
                        continue
                    try:
                        supplier = Supplier.objects.get(id=row[4])
                        Product.objects.create(
                            product_number=row[0],
                            product_name=row[1],
                            cost_price=row[2],
                            sale_price=row[3],
                            supplier=supplier,
                            note=row[5],
                        )
                    except Supplier.DoesNotExist as e:
                        messages.error(request, f"匯入失敗，找不到供應商: {e}")
                        return redirect("products:index")

                messages.success(request, "成功匯入 CSV")
                return redirect("products:index")

            elif file.name.endswith(".xlsx"):
                df = pd.read_excel(file)
                df.rename(
                    columns={
                        "商品編號": "product_number",
                        "商品名稱": "product_name",
                        "商品進價": "cost_price",
                        "商品售價": "sale_price",
                        "供應商名稱": "supplier",
                        "備註": "note",
                    },
                    inplace=True,
                )
                for _, row in df.iterrows():
                    try:
                        supplier = Supplier.objects.get(id=int(row["supplier"]))
                        Product.objects.create(
                            product_number=str(row["product_number"]),
                            product_name=str(row["product_name"]),
                            cost_price=str(row["cost_price"]),
                            sale_price=str(row["sale_price"]),
                            supplier=supplier,
                            note=str(row["note"]) if not pd.isna(row["note"]) else "",
                        )
                    except Supplier.DoesNotExist as e:
                        messages.error(request, f"匯入失敗，找不到供應商: {e}")
                        return redirect("products:index")
                messages.success(request, "成功匯入 Excel")
                return redirect("products:index")

            else:
                messages.error(request, "匯入失敗(檔案不是 CSV 或 Excel)")
                return render(request, "layouts/import.html", {"form": form})

    form = FileUploadForm()
    return render(request, "layouts/import.html", {"form": form})


def export_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="Products.csv"'

    writer = csv.writer(response)
    writer.writerow(
        [
            "序號",
            "商品",
            "價位",
            "供應商",
            "備註",
        ]
    )

    products = Product.objects.all()
    for product in products:
        writer.writerow(
            [
                product.product_number,
                product.product_name,
                product.price,
                product.supplier,
                product.note,
            ]
        )

    return response


def export_excel(request):
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = "attachment; filename=Products.xlsx"

    products = Product.objects.select_related("product", "supplier").values(
        "product_number",
        "product_name",
        "cost_price",
        "sale_price",
        "supplier__name",
        "note",
    )

    df = pd.DataFrame(products)
    for col in df.select_dtypes(include=["datetime64[ns, UTC]"]).columns:
        df[col] = df[col].dt.strftime("%Y-%m-%d %H:%M:%S")

    column_mapping = {
        "product_number": "商品編號",
        "product_name": "商品名稱",
        "cost_price": "商品進價",
        "sale_price": "商品售價",
        "supplier__name": "供應商名稱",
        "note": "備註",
    }

    df.rename(columns=column_mapping, inplace=True)

    with pd.ExcelWriter(response, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Products")
    return response


def export_sample(request):
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = "attachment; filename=ProductSample.xlsx"

    data = {
        "product_number": ["P033"],
        "product_name": ["米"],
        "cost_price": [100],
        "sale_price": [120],
        "supplier": [1],
        "note": ["這是一個備註"],
    }

    df = pd.DataFrame(data)

    with pd.ExcelWriter(response, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Products")

    return response
