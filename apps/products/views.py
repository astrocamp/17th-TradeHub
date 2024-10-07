import csv
from datetime import datetime, timedelta, timezone

import pandas as pd
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.inventory.models import Inventory
from apps.products.models import Product
from apps.sales_orders.models import SalesOrderProductItem
from apps.suppliers.models import Supplier

from .forms.product_form import FileUploadForm, ProductForm


def index(request):
    state = request.GET.get("select")
    order_by = request.GET.get("sort", "id")
    is_desc = request.GET.get("desc", True) == "False"
    state_match = {"often", "haply", "never"}

    products = Product.objects.filter(user=request.user)

    if state in state_match:
        products = Product.objects.filter(state=state, user=request.user)
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
        form = ProductForm(request.POST, user=request.user)
        if form.is_valid():
            product = form.save(commit=False)
            product.user = request.user
            product.save()
            messages.success(request, "新增完成!")
            return redirect("products:index")
    else:
        form = ProductForm(user=request.user)

    return render(request, "products/new.html", {"form": form})


def show(request, id):
    product = get_object_or_404(Product, id=id)
    return render(request, "products/show.html", {"product": product})


def edit(request, id):
    product = get_object_or_404(Product, id=id)
    form = ProductForm(instance=product)
    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "更新完成!")
            return redirect("products:index")
        else:
            return render(
                request, "products/edit.html", {"product": product, "form": form}
            )
    return render(request, "products/edit.html", {"product": product, "form": form})


def delete(request, id):
    product = get_object_or_404(Product, id=id)
    product.delete()
    messages.success(request, "刪除完成!")
    return redirect("products:index")


@require_POST
def import_file(request):
    form = FileUploadForm(request.POST, request.FILES)

    if form.is_valid():
        file = request.FILES["file"]
        try:
            if file.name.endswith(".xlsx"):
                df = pd.read_excel(file)
                df.rename(
                    columns={
                        "商品編號": "number",
                        "商品名稱": "product_name",
                        "商品進價": "cost_price",
                        "商品售價": "sale_price",
                        "供應商名稱": "supplier",
                        "備註": "note",
                    },
                    inplace=True,
                )

                existing_numbers = Product.objects.values_list("number", flat=True)
                if existing_numbers:
                    existing_numbers = [
                        int(num[1:]) for num in existing_numbers if num.startswith("P")
                    ]
                    next_number = max(existing_numbers) + 1
                else:
                    next_number = 1

                for _, row in df.iterrows():
                    try:
                        supplier = Supplier.objects.get(id=int(row["supplier"]))

                        while Product.objects.filter(
                            number=f"P{next_number:03d}"
                        ).exists():
                            next_number += 1

                        Product.objects.create(
                            number=f"P{next_number:03d}",
                            product_name=str(row["product_name"]),
                            cost_price=int(row["cost_price"]),
                            sale_price=int(row["sale_price"]),
                            supplier=supplier,
                            note=str(row["note"]) if not pd.isna(row["note"]) else "",
                            user=request.user,
                        )
                        next_number += 1
                    except Supplier.DoesNotExist:
                        messages.error(
                            request,
                            f"匯入失敗，找不到供應商 ID: {int(row['supplier'])}",
                        )
                        return redirect("products:index")
                    except ValueError:
                        messages.error(
                            request,
                            f"匯入失敗，價格必須是有效的數字: {row['cost_price']}, {row['sale_price']}",
                        )
                        return redirect("products:index")

                messages.success(request, "成功匯入 Excel")
                return redirect("products:index")

            else:
                messages.error(request, "匯入失敗檔案不是 Excel)")
                return render(request, "layouts/import.html", {"form": form})

        except Exception as e:
            messages.error(request, f"匯入失敗: {str(e)}")
            return redirect("products:index")
    else:
        messages.error(request, "表單無效，請檢查上傳的檔案。")
        return redirect("products:index")


def export_excel(request):
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = "attachment; filename=Products.xlsx"

    products = (
        Product.objects.filter(user=request.user)
        .select_related("product", "supplier")
        .values(
            "number",
            "product_name",
            "cost_price",
            "sale_price",
            "supplier__name",
            "note",
        )
    )

    df = pd.DataFrame(products)
    for col in df.select_dtypes(include=["datetime64[ns, UTC]"]).columns:
        df[col] = df[col].dt.strftime("%Y-%m-%d %H:%M:%S")

    column_mapping = {
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
        "product_name": ["米"],
        "cost_price": ["100"],
        "sale_price": ["120"],
        "supplier": ["2"],
        "note": ["這是一個備註"],
    }

    df = pd.DataFrame(data)

    with pd.ExcelWriter(response, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Products")

    return response


@receiver(post_save, sender=Product)
def update_state(sender, instance, **kwargs):
    time_now = datetime.now(timezone(timedelta(hours=+8))).strftime("%Y/%m/%d %H:%M:%S")

    if not Inventory.objects.filter(product=instance).exists():
        Inventory.objects.create(
            product=instance,
            supplier=instance.supplier,
            quantity=0,
            safety_stock=0,
            note=f"{time_now} 新建商品，預建庫存",
            state=Inventory.NEW_STOCK,
            user=instance.user,
        )
    post_save.disconnect(update_state, sender=Product)
    product = SalesOrderProductItem.objects.filter(product=instance.id).count()
    if product == 0:
        instance.set_never()
        instance.save()
    elif product > 0 and product < 3:
        instance.set_haply()
        instance.save()
    elif product > 3:
        instance.set_often()
        instance.save()
    post_save.connect(update_state, sender=Product)
