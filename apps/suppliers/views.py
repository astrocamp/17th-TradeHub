import csv

import pandas as pd
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms.supplier_form import FileUploadForm, SupplierForm
from .models import Supplier


def index(request):
    state = request.GET.get("select")
    order_by = request.GET.get("sort", "id")
    is_desc = request.GET.get("desc", "True") == "False"
    state_match = {"often", "haply", "never"}

    suppliers = Supplier.objects.filter(user=request.user)

    if state in state_match:
        suppliers = Supplier.objects.filter(state=state, user=request.user)
    order_by_field = f"{'-' if is_desc else ''}{order_by or '-id'}"
    suppliers = suppliers.order_by(order_by_field)

    paginator = Paginator(suppliers, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    content = {
        "suppliers": page_obj,
        "selected_state": state,
        "is_desc": is_desc,
        "order_by": order_by,
        "page_obj": page_obj,
    }

    return render(request, "suppliers/index.html", content)


def new(request):
    if request.method == "POST":
        form = SupplierForm(request.POST)
        if form.is_valid():
            supplier = form.save(commit=False)
            supplier.user = request.user
            supplier.save()
            messages.success(request, "新增完成!")
            return redirect("suppliers:index")
        else:
            return render(request, "suppliers/new.html", {"form": form})
    form = SupplierForm()
    return render(request, "suppliers/new.html", {"form": form})


def show(request, id):
    supplier = get_object_or_404(Supplier, pk=id)
    if request.method == "POST":
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, "更新完成!")
            return redirect("suppliers:index")
        else:
            return render(
                request, "suppliers/edit.html", {"supplier": supplier, "form": form}
            )
    return render(request, "suppliers/show.html", {"supplier": supplier})


def edit(request, id):
    supplier = get_object_or_404(Supplier, pk=id)
    form = SupplierForm(instance=supplier)
    return render(request, "suppliers/edit.html", {"supplier": supplier, "form": form})


def delete(request, id):
    supplier = get_object_or_404(Supplier, pk=id)
    supplier.delete()
    messages.success(request, "刪除完成!")
    return redirect("suppliers:index")


@require_POST
def delete_selected_suppliers(request):
    selected_suppliers = request.POST.getlist("selected_suppliers")
    Supplier.objects.filter(id__in=selected_suppliers).delete()
    return redirect("suppliers:index")


def import_file(request):
    if request.method == "POST":
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES["file"]
            try:
                if file.name.endswith(".xlsx"):
                    df = pd.read_excel(file)
                    df.rename(
                        columns={
                            "供應商名稱": "name",
                            "電話": "telephone",
                            "連絡人": "contact_person",
                            "Email": "email",
                            "統一編號": "gui_number",
                            "地址": "address",
                            "備註": "note",
                        },
                        inplace=True,
                    )

                    for _, row in df.iterrows():
                        Supplier.objects.create(
                            name=str(row["name"]),
                            telephone=str(row["telephone"]),
                            contact_person=str(row["contact_person"]),
                            email=str(row["email"]),
                            gui_number=str(row["gui_number"]),
                            address=str(row["address"]),
                            note=str(row["note"]) if not pd.isna(row["note"]) else "",
                            user=request.user,
                        )
                    messages.success(request, "成功匯入 Excel")
                    return redirect("suppliers:index")

                else:
                    messages.error(request, "匯入失敗(檔案不是 CSV 或 Excel)")
                    return render(request, "layouts/import.html", {"form": form})

            except Exception as e:
                messages.error(request, f"匯入失敗: {str(e)}")
                return redirect("suppliers:import_file")

    else:
        form = FileUploadForm()  # Ensure form is instantiated for GET requests
    return redirect("suppliers:index")


def export_excel(request):
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = "attachment; filename=Suppliers.xlsx"

    suppliers = Supplier.objects.filter(user=request.user).values(
        "name",
        "telephone",
        "contact_person",
        "email",
        "gui_number",
        "address",
        "created_at",
        "note",
    )

    df = pd.DataFrame(suppliers)
    for col in df.select_dtypes(include=["datetime64[ns, UTC]"]).columns:
        df[col] = df[col].dt.strftime("%Y-%m-%d %H:%M:%S")

    column_mapping = {
        "name": "供應商名稱",
        "telephone": "電話",
        "contact_person": "連絡人",
        "email": "Email",
        "gui_number": "統一編號",
        "address": "地址",
        "created_at": "建立時間",
        "note": "備註",
    }

    df.rename(columns=column_mapping, inplace=True)

    with pd.ExcelWriter(response, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Suppliers")
    return response


def export_sample(request):
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = "attachment; filename=SuppliersSample.xlsx"

    data = {
        "name": ["好水供應商"],
        "telephone": ["0912-345600"],
        "contact_person": ["大華"],
        "email": ["55dahua@example.com"],
        "gui_number": ["10458574"],
        "address": ["台中市西區建國北路6號"],
        "note": ["我是備註"],
    }

    df = pd.DataFrame(data)

    with pd.ExcelWriter(response, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Suppliers")

    return response
