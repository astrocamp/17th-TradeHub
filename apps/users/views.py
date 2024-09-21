import json

from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt

from .forms.login_form import LoginForm
from .forms.profile_form import ProfileForm
from .forms.user_form import CustomUserCreationForm
from .models import Company, CustomUser

# 取得自定義的 User 模型 CustomUser
User = get_user_model()


def index(request):
    user_form = CustomUserCreationForm()
    return render(request, "users/register.html", {"user_form": user_form})


def register(request):
    if request.method == "POST":
        user_form = CustomUserCreationForm(request.POST)

        if user_form.is_valid():

            user = user_form.save(commit=False)
            user.backend = "django.contrib.auth.backends.ModelBackend"  # 指定後端

            company_name = "個人公司"
            company = Company.objects.create(
                company_name=company_name, id=len(Company.objects.all()) + 1
            )
            user.company = company
            user.save()
            login(request, user)

            return redirect("pages:welcome")

        else:
            return render(request, "users/register.html", {"user_form": user_form})

    user_form = CustomUserCreationForm()
    return render(request, "users/register.html", {"user_form": user_form})


def log_in(request):
    if request.method == "POST":
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            username = login_form.cleaned_data["username"]
            password = login_form.cleaned_data["password"]
            next_url = login_form.cleaned_data.get("next")

            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)

                user.first_login = False
                user.save()

                messages.success(request, "登入成功!")
                return redirect(next_url) if next_url else redirect("pages:home")
            else:
                return render(request, "users/log_in.html", {"login_form": login_form})

        else:
            return render(request, "users/log_in.html", {"login_form": login_form})

    login_form = LoginForm()
    return render(request, "users/log_in.html", {"login_form": login_form})


def log_out(request):
    if request.method == "POST":
        logout(request)
        messages.success(request, "登出成功!")
        return redirect("pages:home")


def reset_password(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        password_confirm = request.POST.get("password_confirm")

        if username:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return render(
                    request,
                    "users/reset_password.html",
                    {"error": "此用戶不存在."},
                )

            if password == password_confirm:
                user.set_password(password)
                user.save()
                user.backend = "django.contrib.auth.backends.ModelBackend"
                login(request, user)
                messages.success(request, "密碼重設成功!")
                return redirect("users:log_in")
            else:
                return render(
                    request,
                    "users/reset_password.html",
                    {"error": "Password does not match."},
                )

        else:
            return render(request, "users/reset_password.html")


def forget_password(request):
    return render(request, "users/reset_password.html")


def profile(request, id):
    user = get_object_or_404(CustomUser, pk=id)
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect("users:profile", id=user.id)
    else:
        form = ProfileForm(instance=user)
    return render(request, "users/profile.html", {"user": user, "form": form})


def edit_profile(request, id):
    user = get_object_or_404(CustomUser, pk=id)

    if request.user != user:
        return redirect("users:profile", user.id)

    if request.method == "POST":
        form = ProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect("users:profile", user.id)
    else:
        form = ProfileForm(instance=user)

    return render(request, "users/edit_profile.html", {"form": form, "user": user})


def update_company_id(request):
    if request.method == "POST":
        gui_number = request.POST.get("gui_number")
        try:
            company = Company.objects.get(gui_number=gui_number)
            user = request.user
            user.company = company
            user.save()
            messages.success(request, f"您已成功註冊至公司：{company.company_name}")
            return redirect("pages:home")
        except Company.DoesNotExist:
            messages.error(request, "此公司尚未註冊")
            return redirect("pages:welcome")
