from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils.crypto import get_random_string

from .decorators import redirect_if_logged_in
from .forms.invitation_form import InvitationRegistrationForm
from .forms.login_form import LoginForm
from .forms.profile_form import ProfileForm
from .forms.user_form import CustomUserCreationForm
from .models import Company, CustomUser, Invitation, Notification

User = get_user_model()


@redirect_if_logged_in
def index(request):
    user_form = CustomUserCreationForm()
    return render(request, "users/register.html", {"user_form": user_form})


@redirect_if_logged_in
def register(request):
    if request.method == "POST":
        user_form = CustomUserCreationForm(request.POST)

        if user_form.is_valid():
            user = user_form.save(commit=False)
            user.backend = "django.contrib.auth.backends.ModelBackend"
            company = Company.objects.get(id=1)
            user.company = company
            user.save()

            write_fake(user)

            messages.success(request, "成功註冊!")
            login(request, user)
            messages.success(request, "註冊成功，並完成登入!")
            return redirect("pages:home")

        else:
            return render(request, "users/register.html", {"user_form": user_form})

    user_form = CustomUserCreationForm()
    return render(request, "users/register.html", {"user_form": user_form})


@redirect_if_logged_in
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
            messages.success(request, "新增完成!")
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
            messages.success(request, "編輯完成!")
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
            messages.success(request, f"您已成功註冊至公司：{company.name}")
            return redirect("pages:home")
        except Company.DoesNotExist:
            messages.error(request, "此公司尚未註冊")
            return redirect("company:new")


def invitation_register(request):
    if request.method == "POST":
        form = InvitationRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "邀約完成!")
            login(request, form)
            return redirect("pages:welcome")
        else:
            return render(request, "users/invitation.html", {"form": form})
    form = InvitationRegistrationForm()
    return render(request, "users/invitation.html", {"form": form})


def send_invitation(request, company_id):
    company = Company.objects.get(id=company_id)
    email = request.POST["email"]
    token = get_random_string(50)
    invitation = Invitation.objects.create(email=email, company=company, token=token)
    registration_url = f"http://yourdomain.com/register?token={token}"

    send_mail(
        "邀請您加入我們的公司",
        f"請點擊以下網址進行註冊:{registration_url}",
        "from@example.com",
        [email],
        fail_silently=False,
    )
    return invitation


def notifications(request):
    notifications_list = Notification.objects.filter(is_read=False).order_by(
        "-created_at"
    )[:5]
    sender_type = request.GET.get("sender_type")
    sender_state = request.GET.get("sender_state")
    unread_count = Notification.objects.filter(is_read=False).count()

    return render(
        request,
        "users/_notifications.html",
        {
            "notifications": notifications_list,
            "sender_type": sender_type,
            "sender_state": sender_state,
            "unread_count": unread_count,
        },
    )


def all_notifications(request):
    page = request.GET.get("page")
    paginator = Paginator(Notification.objects.order_by("-created_at").filter(), 5)
    notifications_list = paginator.get_page(page)
    page_obj = paginator.get_page(page)
    sender_type = request.GET.get("sender_type")
    sender_state = request.GET.get("sender_state")

    content = {
        "notifications": notifications_list,
        "paginator": paginator,
        "page": page,
        "page_obj": page_obj,
        "sender_type": sender_type,
        "sender_state": sender_state,
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

    # notifications = Notification.objects.filter(is_read=False)

    html = render_to_string(
        "users/_notifications_item_all.html",
        {
            "notification": notification,
        },
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


def mark_all_as_read(request):
    Notification.objects.all().update(is_read=True)
    return redirect("users:all_notifications")


def write_fake(user):
    import json
    from apps.suppliers.models import Supplier
    from apps.clients.models import Client
    from apps.products.models import Product
    from apps.inventory.models import Inventory

    with open("./fake_data/suppliers_data.json", "r", encoding="utf-8") as fake:
        template_data = json.load(fake)
    for items in template_data:
        data = items["fields"]
        Supplier.objects.create(
            number=data["number"],
            name=data["name"],
            address=data["address"],
            email=data["email"],
            gui_number=data["gui_number"],
            contact_person=data["contact_person"],
            telephone=data["telephone"],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            note=data["note"],
            user=user,
        )

    with open("./fake_data/clients_data.json", "r", encoding="utf-8") as fake:
        template_data = json.load(fake)
    for items in template_data:
        data = items["fields"]
        Client.objects.create(
            number=data["number"],
            name=data["name"],
            phone_number=data["phone_number"],
            address=data["address"],
            email=data["email"],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            note=data["note"],
            user=user,
        )

    with open("./fake_data/products_data.json", "r", encoding="utf-8") as fake:
        template_data = json.load(fake)
    for items in template_data:
        data = items["fields"]
        Product.objects.create(
            number=data["number"],
            supplier=Supplier.objects.get(pk=data["supplier"]),
            note=data["note"],
            sale_price=data["sale_price"],
            cost_price=data["cost_price"],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            product_name=data["product_name"],
            user=user,
        )

    with open("./fake_data/inventory_data.json", "r", encoding="utf-8") as fake:
        template_data = json.load(fake)
    for items in template_data:
        data = items["fields"]
        Inventory.objects.create(
            number=data["number"],
            product=Product.objects.get(pk=data["product"]),
            supplier=Supplier.objects.get(pk=data["supplier"]),
            quantity=data["quantity"],
            safety_stock=data["safety_stock"],
            created_at=data["created_at"],
            deleted_at=data.get("deleted_at"),
            note=data["note"],
            last_updated=data["last_updated"],
            user=user,
        )
