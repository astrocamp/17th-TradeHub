from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from apps.company.models import Company

from .forms.company_form import CompanyForm


def index(request):
    if request.method == "POST":
        form = CompanyForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("company:index")
        return render(request, "company/new.html", {"form": form})
    company = Company.objects.order_by("-id")
    return render(request, "company/index.html", {"company": company})


def new(request):
    form = CompanyForm
    return render(request, "company/new.html", {"form": form})


def show(request, id):
    company = get_object_or_404(Company, id=id)
    if request.method == "POST":
        form = CompanyForm(request.POST, instance=company)
        if form.is_valid():
            form.save()
            return redirect("company:show", id=id)
        return render(request, "company/edit.html", {"company": company, "form": form})
    return render(request, "company/show.html", {"company": company})


def edit(request, id):
    company = get_object_or_404(Company, id=id)
    form = CompanyForm(instance=company)
    return render(request, "company/edit.html", {"company": company, "form": form})


def delete(request, id):
    company = get_object_or_404(Company, id=id)
    company.delete()
    messages.success(request, "刪除完成!")
    return redirect("company:index")
