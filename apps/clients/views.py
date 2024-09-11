from django.shortcuts import get_object_or_404, redirect, render

from .models import Client


def client_list(req):
    clients = Client.objects.order_by("-id")
    if req.method == "POST":
        phone_number = req.POST.get("phone_number", "")
        if not phone_number.isdigit():
            return render(
                req,
                "list.html",
                {"clients": clients, "error": "請輸入有效的電話號碼。"},
            )
        client = Client(
            name=req.POST["client_name"],
            phone_number=req.POST["phone_number"],
            address=req.POST["address"],
            email=req.POST["email"],
            note=req.POST["note"],
        )
        client.save()
        return redirect("clients:list")
    else:
        return render(req, "list.html", {"clients": clients})


def client_update_and_delete(req, id):
    client = get_object_or_404(Client, id=id)
    if req.method == "POST":
        if "delete" in req.POST:
            client.delete()
            return redirect("clients:list")

        phone_number = req.POST.get("phone_number", "")
        if not phone_number.isdigit():
            return render(
                req, "edit.html", {"client": client, "error": "請輸入有效的電話號碼。"}
            )

        else:
            client.name = req.POST["client_name"]
            client.phone_number = req.POST["phone_number"]
            client.address = req.POST["address"]
            client.email = req.POST["email"]
            client.note = req.POST["note"]

            client.save()
            return redirect("clients:list")

    return render(req, "edit.html", {"client": client})


def index(request):
    state = request.GET.get("select")
    order_by = request.GET.get("sort", "id")
    is_desc = request.GET.get("desc", "True") == "False"
    state_match = {"often", "haply", "never"}

    clients = Client.objects.all()

    if state in state_match:
        clients = Client.objects.filter(state=state)
    order_by_field = order_by if is_desc else "-" + order_by
    clients = clients.order_by(order_by_field)

    content = {
        "clients": clients,
        "selected_state": state,
        "order_by": order_by,
        "is_desc": is_desc,
    }
    return render(request, "list.html", content)
