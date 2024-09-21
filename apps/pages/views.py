from django.shortcuts import render


def out_home(request):
    return render(request, "pages/out_home.html")


def home(req):
    return render(req, "pages/home.html")


def about(req):
    return render(req, "pages/about.html")
