from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView

from .forms.form import ClientForm
from .models import Client


class DataListView(ListView):
    model = Client
    template_name = "clients/list.html"
    context_object_name = "clients"
    paginate_by = 5


def client_list(req):
    clients = Client.objects.order_by("-id")
    return render(req, "clients/list.html", {"clients": clients})


def create(req):
    if req.method == "POST":
        form = ClientForm(req.POST)
        if form.is_valid():
            form.save()
            return redirect("clients:list")
    form = ClientForm()
    return render(req, "clients/create.html", {"form": form})


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
    form = ClientForm(instance=client)
    return render(req, "clients/edit.html", {"client": client, "form": form})
