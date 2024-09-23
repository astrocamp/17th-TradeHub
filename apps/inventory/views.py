import csv
from datetime import datetime, timedelta, timezone

import pandas as pd
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from apps.company.middleware.middleware import get_current_company
from apps.products.models import Product
from apps.purchase_orders.models import ProductItem, PurchaseOrder
from apps.purchase_orders.views import generate_order_number
from apps.suppliers.models import Supplier

from .forms.inventory_form import FileUploadForm, RestockForm
from .models import Inventory


def index(request):

    current_company = get_current_company(request)

    state = request.GET.get("select")
    order_by = request.GET.get("sort", "id")
    is_desc = request.GET.get("desc", "True") == "False"

    inventory = Inventory.objects.filter(company=current_company)

    if state in Inventory.AVAILABLE_STATES:
        inventory = Inventory.objects.filter(company=current_company, state=state)
    order_by_field = order_by if is_desc else "-" + order_by
    inventory = inventory.order_by(order_by_field)

    paginator = Paginator(inventory, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    content = {
        "inventory": page_obj,
        "selected_state": state,
        "is_desc": is_desc,
        "order_by": order_by,
        "page_obj": page_obj,
    }

    return render(request, "inventory/index.html", content)


def new(request):
    current_company = get_current_company(request)
    if request.method == "POST":
        form = RestockForm(request.POST)
        if form.is_valid():
            inventory = form.save(commit=False)
            inventory.company = current_company
            inventory.save()
            messages.success(request, "成功新增!")
            return redirect("inventory:index")
    else:
        form = RestockForm()
    return render(request, "inventory/new.html", {"form": form})


def edit(request, id):
    current_company = get_current_company(request)
    inventory = get_object_or_404(Inventory, id=id, company=current_company)
    if request.method == "POST":
        form = RestockForm(request.POST, instance=inventory)
        if form.is_valid():
            inventory = form.save(commit=False)
            inventory.company = current_company
            inventory.save()
            messages.success(request, "更新完成!")
            return redirect("inventory:index")
    else:
        form = RestockForm(instance=inventory)

    return render(
        request, "inventory/edit.html", {"inventory": inventory, "form": form}
    )


def delete(request, id):
    current_company = get_current_company(request)
    inventory = get_object_or_404(Inventory, id=id, company=current_company)
    inventory.delete()
    messages.success(request, "刪除完成!")
    return redirect("inventory:index")


def import_file(request):
    current_company = get_current_company(request)
    if request.method == "POST":
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES["file"]
            if file.name.endswith(".xlsx"):
                df = pd.read_excel(file)
                df.rename(
                    columns={
                        "商品": "product",
                        "供應商": "supplier",
                        "數量": "quantity",
                        "安全水位": "safety_stock",
                        "備註": "note",
                    },
                    inplace=True,
                )
                for _, row in df.iterrows():
                    try:
                        product = Product.objects.get(id=int(row["product"]))
                        supplier = Supplier.objects.get(id=int(row["supplier"]))
                        Inventory.objects.create(
                            product=product,
                            supplier=supplier,
                            quantity=int(row["quantity"]),
                            safety_stock=int(row["safety_stock"]),
                            note=str(row["note"]) if not pd.isna(row["note"]) else "",
                            company=current_company,
                        )
                    except (Product.DoesNotExist, Supplier.DoesNotExist) as e:
                        messages.error(request, f"匯入失敗，找不到客戶或商品: {e}")
                        return redirect("inventory:index")
                messages.success(request, "成功匯入 Excel")
                return redirect("inventory:index")

            else:
                messages.error(request, "匯入失敗(檔案不是 Excel)")
                return render(request, "layouts/import.html", {"form": form})

    form = FileUploadForm()
    return render(request, "layouts/import.html", {"form": form})


def export_excel(request):
    current_company = get_current_company(request)
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = "attachment; filename=Inventory.xlsx"

    inventory = (
        Inventory.objects.filter(company=current_company)
        .select_related("product", "supplier")
        .values(
            "product__product_name",
            "supplier__name",
            "quantity",
            "safety_stock",
            "last_updated",
            "note",
        )
    )

    df = pd.DataFrame(inventory)
    for col in df.select_dtypes(include=["datetime64[ns, UTC]"]).columns:
        df[col] = df[col].dt.strftime("%Y-%m-%d %H:%M:%S")

    column_mapping = {
        "product__product_name": "商品",
        "supplier__name": "供應商",
        "quantity": "數量",
        "safety_stock": "安全水位",
        "last_updated": "最後更新",
        "note": "備註",
    }

    df.rename(columns=column_mapping, inplace=True)

    with pd.ExcelWriter(response, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Inventory")
    return response


def export_sample(request):
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = "attachment; filename=InventorySample.xlsx"

    data = {
        "product": ["2"],
        "supplier": ["1"],
        "quantity": ["150"],
        "safety_stock": ["30"],
        "note": ["備註"],
    }

    df = pd.DataFrame(data)

    with pd.ExcelWriter(response, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Inventory")

    return response


@receiver(pre_save, sender=Inventory)
def update_state(sender, instance, **kwargs):
    current_company = get_current_company(request)
    time_now = datetime.now(timezone(timedelta(hours=+8))).strftime("%Y/%m/%d %H:%M:%S")
    if instance.safety_stock == 0:
        instance.set_new_stock()
    if instance.quantity <= 0:
        purchase_order = PurchaseOrder.objects.filter(
            supplier=instance.supplier,
            state=PurchaseOrder.PENDING,
            company=current_company,
        )
        if not purchase_order:
            message = f"缺貨，下單{instance.safety_stock}個{instance.product}{time_now}"
            supplier = Supplier.objects.get(name=instance.supplier.name)
            order = PurchaseOrder.objects.create(
                order_number=generate_order_number(),
                supplier=instance.supplier,
                supplier_tel=supplier.telephone,
                contact_person=supplier.contact_person,
                supplier_email=supplier.email,
                amount=0,
                note=message,
                state=PurchaseOrder.PENDING,
                company=current_company,
            )
            orderitem = ProductItem.objects.create(
                purchase_order=order,
                product=instance.product,
                quantity=instance.safety_stock,
                cost_price=instance.product.cost_price,
                subtotal=instance.product.cost_price * instance.safety_stock,
            )
            order.amount = orderitem.subtotal
            order.save()

        else:
            message = f"缺貨，下單{instance.safety_stock}個{instance.product}{time_now}"
            order = PurchaseOrder.objects.get(
                supplier=instance.supplier,
                state=PurchaseOrder.PENDING,
                company=current_company,
            )
            order.note += "\n" + message
            orderitem = ProductItem.objects.create(
                purchase_order=order,
                product=instance.product,
                quantity=instance.safety_stock,
                cost_price=instance.product.cost_price,
                subtotal=instance.product.cost_price * instance.safety_stock,
            )
            order.amount += orderitem.subtotal
            order.save()
        instance.set_out_stock()
    elif instance.quantity < instance.safety_stock:
        purchase_order = PurchaseOrder.objects.filter(
            supplier=instance.supplier,
            state=PurchaseOrder.PENDING,
            company=current_company,
        )
        if not purchase_order:
            message = f"低水位，下單{instance.safety_stock - instance.quantity}個{instance.product}{time_now}"
            supplier = Supplier.objects.get(name=instance.supplier.name)
            order = PurchaseOrder.objects.create(
                order_number=generate_order_number(),
                supplier=instance.supplier,
                supplier_tel=supplier.telephone,
                contact_person=supplier.contact_person,
                supplier_email=supplier.email,
                amount=0,
                note=message,
                state=PurchaseOrder.PENDING,
                company=current_company,
            )
            orderitem = ProductItem.objects.create(
                purchase_order=order,
                product=instance.product,
                quantity=instance.safety_stock - instance.quantity,
                cost_price=instance.product.cost_price,
                subtotal=instance.product.cost_price
                * (instance.safety_stock - instance.quantity),
            )
            order.amount = orderitem.subtotal
            order.save()
        else:
            message = (
                f"低水位，下單{instance.safety_stock}個{instance.product}{time_now}"
            )
            order = PurchaseOrder.objects.get(
                supplier=instance.supplier,
                state=PurchaseOrder.PENDING,
                company=current_company,
                note__contains="低水位",
            )
            order.note += "\n" + message
            orderitem = ProductItem.objects.create(
                purchase_order=order,
                product=instance.product,
                quantity=instance.safety_stock - instance.quantity,
                cost_price=instance.product.cost_price,
                subtotal=instance.product.cost_price
                * (instance.safety_stock - instance.quantity),
            )
            orderitem.quantity += instance.safety_stock - instance.quantity
            order.amount += orderitem.subtotal
            order.save()
        instance.set_low_stock()
    else:
        instance.set_normal()
