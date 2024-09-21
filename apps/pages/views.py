from django.shortcuts import redirect, render


def home(request):
    return render(request, "pages/home.html")


def about(request):
    return render(request, "pages/about.html")


def welcome(request):
    if request.session.get("has_seen_welcome", False):
        return redirect("pages:home")

    request.session["has_seen_welcome"] = True
    return render(request, "pages/welcome.html")
