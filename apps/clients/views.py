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
