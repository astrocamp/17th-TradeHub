from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.company.models import Company

from .forms.company_form import CompanyForm


def index(request):
    if request.method == "POST":
        form = CompanyForm(request.POST)
        if form.is_valid():
            company = form.save(commit=False)
            company.created_at = timezone.now()
            company.save()

            request.user.company = company
            request.user.is_superuser = True
            request.user.save()
            request.session["company_id"] = request.user.company_id

            messages.success(request, "公司帳號新增成功!")
            return redirect("company:show", id=company.id)
        return render(request, "company/new.html", {"form": form})
    else:
        return redirect("company:show", id=company.id)


def new(request):
    form = CompanyForm()
    if request.user.company:
        if request.user.company.company_name == "個人公司":
            return render(request, "company/new.html", {"form": form})
        else:
            messages.success(request, "您已經有公司帳號了!")
            return redirect("pages:home")
    else:
        messages.success(request, "您還沒有公司帳號!")
        return render(request, "company/new.html", {"form": form})


def show(request, id):
    company = get_object_or_404(Company, id=id)
    if request.user.company is None:
        messages.success(request, "您還沒有公司帳號!")
        return redirect("company:index")
    if request.user.company != company:
        return redirect("pages:home")
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
