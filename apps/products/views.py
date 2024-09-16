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
    order_by_field = f"{'-' if is_desc else ''}{order_by}"
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
    return redirect("products:index")


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
                    if len(row) < 5:
                        # messages.error(request, f"CSV 数据不完整，跳过该行: {row}") 很奇怪?
                        # IndexError: list index out of range
                        continue
                    try:
                        supplier = Supplier.objects.get(id=row[3])
                        Product.objects.create(
                            product_id=row[0],
                            product_name=row[1],
                            price=row[2],
                            supplier=supplier,
                            note=row[4],
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
                        "序號": "product_id",
                        "產品": "product_name",
                        "價位": "price",
                        "供應商": "supplier",
                        "備註": "note",
                    },
                    inplace=True,
                )
                for _, row in df.iterrows():
                    try:
                        supplier = Supplier.objects.get(id=int(row["supplier"]))
                        Product.objects.create(
                            product_id=str(row["product_id"]),
                            product_name=str(row["product_name"]),
                            price=str(row["price"]),
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
            "產品",
            "價位",
            "供應商",
            "備註",
        ]
    )

    products = Product.objects.all()
    for product in products:
        writer.writerow(
            [
                product.product_id,
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
        "product_id",
        "product_name",
        "price",
        "supplier__name",
        "note",
    )

    df = pd.DataFrame(products)
    for col in df.select_dtypes(include=["datetime64[ns, UTC]"]).columns:
        df[col] = df[col].dt.strftime("%Y-%m-%d %H:%M:%S")

    column_mapping = {
        "product_id": "序號",
        "product_name": "產品",
        "price": "價位",
        "supplier__name": "供應商",
        "note": "備註",
    }

    df.rename(columns=column_mapping, inplace=True)

    with pd.ExcelWriter(response, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Products")
    return response
