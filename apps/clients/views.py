import csv

import pandas as pd
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms.clients_form import ClientForm, FileUploadForm
from .models import Client


def index(request):
    state = request.GET.get("select")
    order_by = request.GET.get("sort")
    is_desc = request.GET.get("desc", "True") == "False"
    state_match = {"often", "haply", "never"}

    clients = Client.objects.all()

    if state in state_match:
        clients = Client.objects.filter(state=state)
    order_by_field = f"{'-' if is_desc else ''}{order_by or 'id'}"
    clients = clients.order_by(order_by_field)

    paginator = Paginator(clients, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    content = {
        "clients": page_obj,
        "selected_state": state,
        "is_desc": is_desc,
        "order_by": order_by,
        "page_obj": page_obj,
    }

    return render(request, "clients/index.html", content)


def new(request):
    if request.method == "POST":
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("clients:index")
        else:
            return render(request, "clients/new.html", {"form": form})
    form = ClientForm()
    return render(request, "clients/new.html", {"form": form})


def client_update_and_delete(request, id):
    client = get_object_or_404(Client, id=id)
    if request.method == "POST":
        if "delete" in request.POST:
            client.delete()
            messages.success(request, "刪除完成!")
            return redirect("clients:index")
        else:
            form = ClientForm(request.POST, instance=client)
            if form.is_valid():
                form.save()
                return redirect("clients:index")
            else:
                return render(
                    request, "clients/edit.html", {"client": client, "form": form}
                )
    form = ClientForm(instance=client)
    return render(request, "clients/edit.html", {"client": client, "form": form})


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
                    Client.objects.create(
                        name=row[0],
                        phone_number=row[1],
                        address=row[2],
                        email=row[3],
                        note=row[4],
                    )
                messages.success(request, "CSV檔案已成功匯入")
                return redirect("clients:index")

            elif file.name.endswith(".xlsx"):
                df = pd.read_excel(file, dtype={"phone_number": str})
                for _, row in df.iterrows():
                    Client.objects.create(
                        name=str(row["name"]),
                        phone_number=str(row["phone_number"]),
                        address=str(row["address"]),
                        email=str(row["email"]),
                        note=str(row["note"]) if not pd.isna(row["note"]) else "",
                    )

                messages.success(request, "成功匯入 Excel")
                return redirect("clients:index")

            else:
                messages.error(request, "匯入失敗(檔案不是 CSV 或 Excel)")
                return render(request, "layouts/import.html", {"form": form})

    form = FileUploadForm()
    return render(request, "layouts/import.html", {"form": form})


def export_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="Clients.csv"'

    writer = csv.writer(response)
    writer.writerow(
        ["客戶名稱", "電話", "地址", "Email", "建立時間", "刪除時間", "備註"]
    )

    clients = Client.objects.all()
    for client in clients:
        writer.writerow(
            [
                client.name,
                client.phone_number,
                client.address,
                client.email,
                client.create_at,
                client.delete_at,
                client.note,
            ]
        )

    return response


def export_excel(request):
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = "attachment; filename=Clients.xlsx"

    clients = Client.objects.all().values(
        "name", "phone_number", "address", "email", "create_at", "delete_at", "note"
    )

    df = pd.DataFrame(clients)
    for col in df.select_dtypes(include=["datetime64[ns, UTC]"]).columns:
        df[col] = df[col].dt.strftime("%Y-%m-%d %H:%M:%S")

    column_mapping = {
        "name": "客戶名稱",
        "phone_number": "電話",
        "address": "地址",
        "email": "Email",
        "create_at": "建立時間",
        "delete_at": "刪除時間",
        "note": "備註",
    }

    df.rename(columns=column_mapping, inplace=True)

    with pd.ExcelWriter(response, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Clients")

    return response


def export_sample(request):
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = "attachment; filename=ClientsSample.xlsx"

    data = {
        "name": ["陳小明"],
        "phone_number": ["0914408235"],
        "address": [
            "台北市中正區XX路XX號",
        ],
        "email": ["alice@example.com"],
        "note": ["這是另一個備註"],
    }

    df = pd.DataFrame(data)

    with pd.ExcelWriter(response, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Clients")

    return response
