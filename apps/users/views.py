from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.shortcuts import redirect, render

from .forms.user_form import CustomUserCreationForm

# 取得自定義的 User 模型 CustomUser
User = get_user_model()


def index(req):
    # 送出註冊表單
    if req.method == "POST":
        form = CustomUserCreationForm(req.POST)

        if form.is_valid():
            form.save()
            login(req, form.instance)
            messages.success(req, "Successfully registered.")
            return redirect("pages:home")
        else:
            return render(req, "users/register.html", {"form": form})

    # 跳轉到登入頁面
    return redirect("users:log_in")


def register(req):
    # 註冊頁面
    form = CustomUserCreationForm()
    return render(req, "users/register.html", {"form": form})


def log_in(req):
    # 送出登入表單
    if req.method == "POST":
        username = req.POST.get("username")
        password = req.POST.get("password")
        next_url = req.POST.get("next")

        user = authenticate(username=username, password=password)

        if user is not None:
            login(req, user)
            messages.success(req, "Successfully logged in.")
            if next_url:
                return redirect(next_url)

            return redirect("pages:home")
        else:
            return render(req, "users/log_in.html")

    return render(req, "users/log_in.html")


def log_out(req):
    # 登出
    if req.method == "POST":
        logout(req)
        messages.success(req, "Successfully logged out.")
        return redirect("pages:home")


def profile(req):
    # 職員資料頁面，未完成
    return render(req, "users/profile.html")


def reset_password(req):
    # 送出重設密碼表單
    if req.method == "POST":
        username = req.POST.get("username")
        password = req.POST.get("password")
        password_confirm = req.POST.get("password_confirm")

        # 檢查帳號是否存在
        if username:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return render(
                    req, "users/reset_password.html", {"error": "User does not exist."}
                )

            # 檢查密碼是否一致
            if password == password_confirm:
                user.set_password(password)
                user.save()
                login(req, user)
                return redirect("users:log_in")
            else:
                return render(
                    req,
                    "users/reset_password.html",
                    {"error": "Password does not match."},
                )

        else:
            return render(req, "users/reset_password.html")


def forget_password(req):
    return render(req, "users/reset_password.html")
