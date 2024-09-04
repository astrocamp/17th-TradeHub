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
    return render(req, "clients/edit.html", {"clients": clients})


def create(request):
    if request.method == "POST":
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("clients:list")
    form = ClientForm()
    return render(request, "clients/create.html", {"form": form})


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

    content = {
        "clients": clients,
        "selected_state": state,
        "is_desc": is_desc,
        "order_by": order_by,
    }

    return render(request, "clients/list.html", content)
