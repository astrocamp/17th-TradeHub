import csv

import pandas as pd
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms.form import FileUploadForm, SupplierForm
from .models import Supplier


def index(request):
    state = request.GET.get("select")
    order_by = request.GET.get("sort", "id")
    is_desc = request.GET.get("desc", "True") == "False"
    state_match = {"often", "haply", "never"}

    suppliers = Supplier.objects.all()

    if state in state_match:
        suppliers = Supplier.objects.filter(state=state)
        order_by_field = order_by if is_desc else "-" + order_by
        suppliers = suppliers.order_by(order_by_field)
        paginator = Paginator(suppliers, 5)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

    # suppliers = Supplier.objects.order_by("id")
    paginator = Paginator(suppliers, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    content = {
        "suppliers": suppliers,
        "selected_state": state,
        "order_by": order_by,
        "is_desc": is_desc,
        "suppliers": page_obj,
        "page_obj": page_obj,
    }

    return render(request, "suppliers/index.html", content)


def new(request):
    if request.method == "POST":
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
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
    form = FileUploadForm(request.POST, request.FILES)
    if form.is_valid():
        file = request.FILES["file"]
        if file.name.endswith(".csv"):

            decoded_file = file.read().decode("utf-8").splitlines()
            reader = csv.reader(decoded_file)
            next(reader)
            try:

                for row in reader:
                    if len(row) < 7:
                        continue
                    Supplier.objects.create(
                        name=row[0],
                        telephone=row[1],
                        contact_person=row[2],
                        email=row[3],
                        gui_number=row[4],
                        address=row[5],
                        note=row[6],
                    )
                messages.success(request, "成功匯入 CSV")
                return redirect("suppliers:index")
            except:
                messages.error(request, "匯入失敗(CSV 裡格式或名稱有問題)")
                return redirect("suppliers:import_file")

        elif file.name.endswith(".xlsx"):
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
            try:
                for _, row in df.iterrows():
                    Supplier.objects.create(
                        name=str(row["name"]),
                        telephone=str(row["telephone"]),
                        contact_person=str(row["contact_person"]),
                        email=str(row["email"]),
                        gui_number=str(row["gui_number"]),
                        address=str(row["address"]),
                        note=str(row["note"]) if not pd.isna(row["note"]) else "",
                    )
                messages.success(request, "成功匯入 Excel")
                return redirect("suppliers:index")
            except:
                messages.success(request, "失敗匯入(Excel裡格式或名稱有問題)")
                return redirect("suppliers:import_file")

        else:
            messages.error(request, "匯入失敗(檔案不是 CSV 或 Excel)")
            return render(request, "layouts/import.html", {"form": form})

    form = FileUploadForm()
    return render(request, "layouts/import.html", {"form": form})


def export_csv(request):
    response = HttpResponse(content_type="csv")
    response["Content-Disposition"] = 'attachment; filename="Suppliers.csv"'

    writer = csv.writer(response)
    writer.writerow(
        [
            "供應商名稱",
            "電話",
            "連絡人",
            "Email",
            "統一編號",
            "地址",
            "建立時間",
            "備註",
        ]
    )

    suppliers = Supplier.objects.all()
    for supplier in suppliers:
        writer.writerow(
            [
                supplier.name,
                supplier.telephone,
                supplier.contact_person,
                supplier.email,
                supplier.gui_number,
                supplier.address,
                supplier.created_at,
                supplier.note,
            ]
        )

    return response


def export_excel(request):
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = "attachment; filename=Suppliers.xlsx"

    suppliers = Supplier.objects.all().values(
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
        "name": ["供應商Y"],
        "telephone": ["0912-345600"],
        "contact_person": ["大華"],
        "email": ["55dahua@example.com"],
        "gui_number": ["10458574"],
        "address": ["台中市西區建國北路6號"],
        "note": ["備註"],
    }

    df = pd.DataFrame(data)

    with pd.ExcelWriter(response, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Suppliers")

    return response
