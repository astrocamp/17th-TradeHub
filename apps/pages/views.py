from django.shortcuts import render


def home(req):
    return render(req, "apps/pages/home.html")


def about(req):
    return render(req, "apps/pages/about.html")
