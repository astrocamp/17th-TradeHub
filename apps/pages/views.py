from django.shortcuts import render


def home(req):
    return render(req, "pages/home.html")


def about(req):
    return render(req, "pages/about.html")
