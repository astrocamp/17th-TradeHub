from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms.clients_form import ClientForm
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

    return render(request, "clients/list.html", content)


def new(request):
    if request.method == "POST":
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("clients:index")
        else:
            return render(request, "clients/create.html", {"form": form})
    form = ClientForm()
    return render(request, "clients/create.html", {"form": form})


def client_update_and_delete(request, id):
    client = get_object_or_404(Client, id=id)
    if request.method == "POST":
        if "delete" in request.POST:
            client.delete()
            return redirect("clients:index")
        else:
            form = ClientForm(request.POST, instance=client)
            if form.is_valid():
                form.save()
                return redirect("clients:index")
    form = ClientForm(instance=client)
    return render(request, "clients/edit.html", {"client": client, "form": form})
