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
            MinLengthValidator(8, message="密碼至少8個字元"),
            RegexValidator(
                regex=r"^[A-Za-z0-9]+$",
                message="密碼至少包含一個數字和一個字母",
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

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if username == "":
            raise forms.ValidationError("請輸入您的帳號")
        elif CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError("這個帳號已被使用")
        elif len(username) < 6:
            raise forms.ValidationError("帳號至少6個字元")
        elif not username.isalnum():
            raise forms.ValidationError("帳號只能包含數字和字母")
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
        password1 = self.cleaned_data.get("password1")
        if password2 == "":
            raise forms.ValidationError("請再次輸入您的密碼")
        if password1 != password2:
            raise forms.ValidationError("兩次密碼不一致")

        return password2

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email == "":
            raise forms.ValidationError("請輸入您的Email信箱")
        return email
