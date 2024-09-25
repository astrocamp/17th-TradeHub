from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string

from .forms.login_form import LoginForm
from .forms.profile_form import ProfileForm
from .forms.user_form import CustomUserCreationForm
from .models import CustomUser, Notification

# 取得自定義的 User 模型 CustomUser
User = get_user_model()


def index(request):
    user_form = CustomUserCreationForm()
    return render(request, "users/register.html", {"user_form": user_form})


def register(request):
    if request.method == "POST":
        user_form = CustomUserCreationForm(request.POST)
        username = request.POST.get("username")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        email = request.POST.get("email")

        if user_form.is_valid():

            user = user_form.save()
            user.backend = "django.contrib.auth.backends.ModelBackend"  # 指定後端

            login(request, user)
            messages.success(request, "成功註冊！")
            return redirect("pages:home")

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
                messages.success(request, "成功登入！")
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
        messages.success(request, "成功登出！")
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
                    {"error": "此帳號不存在"},
                )

            if password == password_confirm:
                user.set_password(password)
                user.save()
                user.backend = "django.contrib.auth.backends.ModelBackend"
                login(request, user)
                messages.success(request, "成功修改密碼！")
                return redirect("users:log_in")
            else:
                return render(
                    request,
                    "users/reset_password.html",
                    {"error": "密碼不一致"},
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


def notifications(request):
    # 限制為五筆
    notifications_list = Notification.objects.order_by("-created_at")[:4]
    sender_type = request.GET.get("sender_type")
    sender_state = request.GET.get("sender_state")
    unread_count = Notification.objects.filter(is_read=False).count()

    if sender_type and sender_state:
        Notification.objects.filter(
            sender_type=sender_type, sender_state=sender_state
        ).update(is_read=True)

    return render(
        request,
        "users/_notifications.html",
        {
            "notifications": notifications_list,
            "sender_type": sender_type,
            "unread_count": unread_count,
        },
    )


def all_notifications(request):
    page = request.GET.get("page")
    paginator = Paginator(Notification.objects.order_by("-created_at"), 5)
    notifications_list = paginator.get_page(page)
    page_obj = paginator.get_page(page)

    content = {
        "notifications": notifications_list,
        "paginator": paginator,
        "page": page,
        "page_obj": page_obj,
    }

    return render(
        request,
        "users/notifications.html",
        content,
    )


def mark_as_read(request, notification_id):
    notification = get_object_or_404(Notification, pk=notification_id)
    notification.is_read = True
    notification.save()

    html = render_to_string(
        "users/_notifications_item.html", {"notification": notification}
    )
    return HttpResponse(html)


def mark_as_read_fullpage(request, notification_id):
    notification = get_object_or_404(Notification, pk=notification_id)
    notification.is_read = True
    notification.save()

    html = render_to_string(
        "users/_notifications_item_all.html", {"notification": notification}
    )
    return HttpResponse(html)


def unread_count(request):
    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(
            is_read=False, user=request.user
        ).count()
        return JsonResponse({"unread_count": unread_count})
    else:
        return JsonResponse({"unread_count": 0})
