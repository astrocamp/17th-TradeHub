from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import DateInput, TextInput
from django.utils import timezone

from apps.users.models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control w-full input input-bordered",
                "placeholder": "Please enter your name.",
            }
        ),
        label="Name",
    )
    birthday = forms.DateField(
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": "form-control w-full input input-bordered",
                "placeholder": "Please enter your birth date.",
            }
        ),
        label="Birthday",
    )
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "class": "form-control w-full input input-bordered",
                "placeholder": "Please enter your email.",
            }
        ),
        label="Email",
    )
    phone = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control w-full input input-bordered",
                "placeholder": "Please enter your phone number.",
            }
        ),
        label="Phone",
    )
    address = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control w-full input input-bordered",
                "placeholder": "Please enter your address.",
            }
        ),
        label="Address",
    )
    title = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control w-full input input-bordered",
                "placeholder": "Please enter your title.",
            }
        ),
        label="Title",
    )

    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control w-full input input-bordered",
                "placeholder": "Please enter your username.",
            }
        ),
        label="Username",
    )

    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control w-full input input-bordered",
                "placeholder": "Please enter your password.",
            }
        ),
        label="Password",
        help_text="Password must be at least 8 characters long, and cannot be entirely numeric.",
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control w-full input input-bordered",
                "placeholder": "Please confirm your password again.",
            }
        ),
        label="Confirm Password",
        help_text="The passwords must match.",
    )

    # 欄位拉出meta，才會顯示出必填
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = [
            "first_name",
            "birthday",
            "email",
            "phone",
            "address",
            "title",
            "hire_date",
            "username",
            "password1",
            "password2",
        ]
        widgets = {
            "hire_date": DateInput(
                attrs={
                    "class": "form-control w-full input input-bordered text-gray-300",
                    "readonly": "readonly",
                    "value": timezone.now().strftime("%Y-%m-%d"),
                }
            ),
            "note": TextInput(
                attrs={
                    "class": "form-control w-full input input-bordered",
                    "placeholder": "Any additional information.",
                }
            ),
        }
        labels = {
            "hire_date": "Hire Date",
            "note": "Note",
        }

        # 初始化方法，用於在表單實例化時做初始設定
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        # ----------------這段目前看起來沒成功----------------------
        # cleaned_data 方法可用來儲存經過驗證的數據，可以用來加強驗證邏輯
        # UserCreationForm 預設已包含檢查兩次密碼是否一致，帳號是否已存在
        def clean_password2(self):
            password2 = self.cleaned_data.get("password2")

            # 檢查密碼長度和內容
            if len(password2) < 8:
                raise forms.ValidationError(
                    "Password must be at least 8 characters long."
                )
            if not any(char.isdigit() for char in password2):
                raise forms.ValidationError(
                    "Password must contain at least one number."
                )
            if not any(char.isalpha() for char in password2):
                raise forms.ValidationError(
                    "Password must contain at least one letter."
                )

            return password2

        # 檢查 email 是否已存在
        def clean_email(self):
            email = self.cleaned_data.get("email")
            if CustomUser.objects.filter(email=email).exists():
                raise forms.ValidationError("Email already exists")
            return email

        # 檢查帳號長度，至少6個字符
        def clean_username(self):
            username = self.cleaned_data.get("username")
            if len(username) < 6:
                raise forms.ValidationError(
                    "Username must be at least 6 characters long."
                )
            return username
