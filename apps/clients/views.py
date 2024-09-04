from django.shortcuts import get_object_or_404, redirect, render

from .forms.form import ClientForm
from .models import Client


def client_list(req):
    clients = Client.objects.order_by("-id")
    if req.method == "POST":
        form = ClientForm(req.POST)
        if form.is_valid():
            form.save()
            return redirect("clients:list")
        return render(req, "clients/list.html", {"clients": clients, "form": form})
    form = ClientForm()
    return render(req, "clients/list.html", {"clients": clients, "form": form})


def client_update_and_delete(req, id):
    client = get_object_or_404(Client, id=id)
    if req.method == "POST":
        if "delete" in req.POST:
            client.delete()
            return redirect("clients:list")
        else:
            form = ClientForm(req.POST, instance=client)
            if form.is_valid():
                form.save()
                return redirect("clients:list")
            return render(req, "clients/edit.html", {"client": client, "form": form})
    form = ClientForm(instance=client)
    return render(req, "clients/edit.html", {"client": client, "form": form})
