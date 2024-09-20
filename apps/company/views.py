from django.shortcuts import render, get_object_or_404, redirect
from apps.company.models import Company
from .forms.company_form import CompanyForm

def index(request):
    if request.method == "POST":
        form = CompanyForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("company:index")
        return render(request, "company/new.html", {"form":form})
    company = Company.objects.order_by("-id")
    return render(request, "company/index.html", {"company":company})

def new(request):
    form = CompanyForm
    return render(request, "company/new.html", {"form":form})
