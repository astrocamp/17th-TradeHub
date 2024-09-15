from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import MinLengthValidator, RegexValidator
from django.forms import DateInput, TextInput
from django.utils import timezone

from apps.users.models import CustomUser


class CustomUserCreationForm(UserCreationForm):

    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control w-full input input-bordered",
                "placeholder": "請輸入您的密碼",
            }
        ),
        validators=[
            MinLengthValidator(8, message="密碼至少8個字元。"),
            RegexValidator(
                regex=r"^[A-Za-z0-9]+$",
                message="密碼至少包含一個數字和一個字母。",
            ),
        ],
        label="密碼",
        help_text="密碼至少8個字元，且需包含數字和字母",
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control w-full input input-bordered",
                "placeholder": "請再次輸入您的密碼",
            }
        ),
        label="確認密碼",
        help_text="兩次密碼必須相同",
    )

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = [
            "username",
            "password1",
            "password2",
            "email",
        ]
        widgets = {
            "username": forms.TextInput(
                attrs={
                    "class": "form-control w-full input input-bordered",
                    "placeholder": "請輸入您的帳號",
                },
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control w-full input input-bordered",
                    "placeholder": "purchasing@tradehub.com",
                }
            ),
        }
        labels = {
            "username": "帳號",
            "email": "Email",
        }
        help_texts = {
            "username": "帳號至少6個字元",
            "email": "必須是有效的電子郵件格式",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False

    # cleaned_data 方法可用來儲存經過驗證的數據，可以用來加強驗證邏輯
    # UserCreationForm 預設已包含檢查兩次密碼是否一致，帳號是否已存在

    # raise ValidationError 會迅速終止驗證，避免不必要的驗證
    def clean_username(self):
        username = self.cleaned_data.get("username")
        if username == "":
            raise forms.ValidationError("請輸入您的帳號")
        elif CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError("這個帳號已被使用")
        elif len(username) < 6:
            raise forms.ValidationError("帳號至少6個字元")
        return username

    def clean_password1(self):
        password1 = self.cleaned_data.get("password1")

        if password1 == "":
            raise forms.ValidationError("請輸入您的密碼")
        elif len(password1) < 8:
            raise forms.ValidationError("密碼至少8個字元")
        elif password1.isdigit() or password1.isalpha():
            raise forms.ValidationError("密碼不能全是數字或字母")

        return password1

    def clean_password2(self):
        password2 = self.cleaned_data.get("password2")

        if password2 == "":
            raise forms.ValidationError("請再次輸入您的密碼")

        return password2

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email == "":
            raise forms.ValidationError("請輸入您的Email信箱")
        elif CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("這個Email信箱已被使用")
        return email
