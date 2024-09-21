from django.shortcuts import redirect, render


def home(request):
    if request.user.first_login:
        request.user.first_login = False
        request.user.save()
        return render(request, "pages/home.html", {"first_login": True})
    return render(request, "pages/home.html")


def about(request):
    return render(request, "pages/about.html")


def welcome(request):
    if request.session.get("has_seen_welcome", False):
        return redirect("pages:home")

    request.session["has_seen_welcome"] = True
    return render(request, "pages/welcome.html")
