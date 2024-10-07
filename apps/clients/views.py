import csv

import pandas as pd
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.sales_orders.models import SalesOrder

from .forms.clients_form import ClientForm, FileUploadForm
from .models import Client


def index(request):
    state = request.GET.get("select")
    order_by = request.GET.get("sort")
    is_desc = request.GET.get("desc", "True") == "False"
    state_match = {"often", "haply", "never"}

    clients = Client.objects.filter(user=request.user)

    if state in state_match:
        clients = Client.objects.filter(state=state, user=request.user)
    order_by_field = f"{'-' if is_desc else ''}{order_by or '-id'}"
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
            client = form.save(commit=False)
            client.user = request.user
            client.save()

            messages.success(request, "新增完成!")
            return redirect("clients:index")
        else:
            return render(request, "clients/new.html", {"form": form})
    form = ClientForm()
    return render(request, "clients/new.html", {"form": form})


def show(request, id):
    client = get_object_or_404(Client, id=id)
    return render(request, "clients/show.html", {"client": client})


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
                messages.success(request, "更新完成!")
                return redirect("clients:index")
            else:
                return render(
                    request, "clients/edit.html", {"client": client, "form": form}
                )
    form = ClientForm(instance=client)
    return render(request, "clients/edit.html", {"client": client, "form": form})


def delete(request, id):
    client = get_object_or_404(Client, id=id)
    client.delete()
    messages.success(request, "刪除完成!")
    return redirect("clients:index")


def import_file(request):
    form = FileUploadForm(request.POST, request.FILES)

    if form.is_valid():
        file = request.FILES["file"]

        try:
            if file.name.endswith(".xlsx"):
                df = pd.read_excel(file, dtype={"phone_number": str})

                last_client = Client.objects.order_by("-id").first()
                next_number = 1 if not last_client else int(last_client.number[1:]) + 1

                for _, row in df.iterrows():
                    Client.objects.create(
                        number=f"C{next_number:03d}",
                        name=str(row["name"]),
                        phone_number=str(row["phone_number"]),
                        address=str(row["address"]),
                        email=str(row["email"]),
                        note=str(row["note"]) if not pd.isna(row["note"]) else "",
                        user=request.user,
                    )
                    next_number += 1  # Increment for the next client

                messages.success(request, "成功匯入 Excel")
                return redirect("clients:index")

            else:
                messages.error(request, "匯入失敗 檔案不是 Excel")
                return render(request, "layouts/import.html", {"form": form})

        except Exception as e:
            messages.error(request, f"匯入失敗: {str(e)}")
            return redirect("clients:index")
    else:
        messages.error(request, "表單無效，請檢查上傳的檔案。")
        return redirect("clients:index")


def export_excel(request):
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = "attachment; filename=Clients.xlsx"

    clients = Client.objects.filter(user=request.user).values(
        "name",
        "phone_number",
        "address",
        "email",
        "created_at",
        "note",
    )

    df = pd.DataFrame(clients)
    for col in df.select_dtypes(include=["datetime64[ns, UTC]"]).columns:
        df[col] = df[col].dt.strftime("%Y-%m-%d %H:%M:%S")

    column_mapping = {
        "name": "客戶名稱",
        "phone_number": "電話",
        "address": "地址",
        "email": "Email",
        "created_at": "建立時間",
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


@receiver(post_save, sender=Client)
def update_state(sender, instance, **kwargs):
    post_save.disconnect(update_state, sender=Client)
    order = SalesOrder.objects.filter(client=instance.id).count()
    if order == 0:
        instance.set_never()
    elif order > 0 and order < 3:
        instance.set_haply()
    elif order > 3:
        instance.set_often()
    instance.save()
    post_save.connect(update_state, sender=Client)
