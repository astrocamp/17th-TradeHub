from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.shortcuts import redirect, render
from .forms.user_form import CustomUserCreationForm

# 取得自定義的 User 模型 CustomUser
User = get_user_model()


def index(req):
    if req.method == "POST":
        # u1 = CustomUser(username=req.POST.get('username'), password=req.POST.get('password1'))
        # u1.save()
        form = CustomUserCreationForm(req.POST)
        if form.is_valid():
            form.save()
            login(req, form.instance)
            return redirect("pages:home")
        else:
            return render(req, "users/register.html", {"form": form})

def register(req):
    form = CustomUserCreationForm()
    return render(req, "users/register.html", {"form": form})

def log_in(req):
    if req.method == "POST":
        username = req.POST.get("username")
        password = req.POST.get("password")
        next_url = req.POST.get("next")

        user = authenticate(username=username, password=password)

        if user is not None:
            login(req, user)
            messages.success(req, "登入成功")
            if next_url:
                return redirect(next_url)

            return redirect("pages:home")
        else:
            return render(req, "users/log_in.html")

    return render(req, "users/log_in.html")


def log_out(req):
    if req.method == "POST":
        logout(req)
        messages.success(req, "登出成功")
        return redirect("pages:home")
    
def profile(req):
    return render(req, "users/profile.html")

def reset_password(req):
    if req.method == "POST":
        pass

def forget_password(req):
    return render(req, "users/reset_password.html")