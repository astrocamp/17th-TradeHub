from django.shortcuts import render, redirect, get_object_or_404
from .models import Client


def client_list(req):
    clients = Client.objects.order_by("-id")
    if req.method == "POST":
        client = Client(
            name=req.POST["client_name"],
            phone_number=req.POST["phone_number"],
            address=req.POST["address"],
            email=req.POST["email"],
            note=req.POST["note"],
        )
        client.save()
        return redirect("client:list")
    else:
        return render(req, "list.html", {"clients": clients})


def client_update_and_delete(req, id):
    client = get_object_or_404(Client, id=id)
    if req.method == "POST":
        if "delete" in req.POST:
            client.delete()
            return redirect("client:list")

        else:
            client.name = req.POST["client_name"]
            client.phone_number = req.POST["phone_number"]
            client.address = req.POST["address"]
            client.email = req.POST["email"]
            client.note = req.POST["note"]

            client.save()
            return redirect("client:list")

    return render(req, "edit.html", {"client": client})
