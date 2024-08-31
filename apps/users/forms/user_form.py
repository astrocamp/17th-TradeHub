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
                "placeholder": "請輸入您的姓名",
            }
        ),
        label="姓名",
    )
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "class": "form-control w-full input input-bordered",
                "placeholder": "請輸入您的電子郵件",
            }
        ),
        label="電子郵件",
    )
    phone = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control w-full input input-bordered",
                "placeholder": "請輸入您的電話號碼",
            }
        ),
        label="電話",
    )
    address = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control w-full input input-bordered",
                "placeholder": "請輸入您的地址",
            }
        ),
        label="地址",
    )
    title = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control w-full input input-bordered",
                "placeholder": "請輸入您的職稱",
            }
        ),
        label="職稱",
    )

    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control w-full input input-bordered",
                "placeholder": "請輸入您的帳號",
            }
        ),
        label="帳號",
    )

    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control w-full input input-bordered",
                "placeholder": "請輸入您的密碼",
            }
        ),
        label="密碼",
        help_text=" 密碼至少包含8個字元，且包含數字、英文字母",
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control w-full input input-bordered",
                "placeholder": "請再次確認您的密碼",
            }
        ),
        label="確認密碼",
        help_text=" 兩次輸入的密碼必須一致",
    )

    # 欄位拉出meta，才會顯示出必填
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = [
            "first_name",
            "email",
            "phone",
            "address",
            "title",
            "hire_date",
            "note",
            "username",
            "password1",
            "password2",
        ]
        widgets = {
            "hire_date": DateInput(
                attrs={
                    "class": "form-control w-full input input-bordered text-gray-300",
                    "placeholder": "請選擇您的入職時間",
                    "readonly": "readonly",
                    "value": timezone.now().strftime("%Y-%m-%d"),
                }
            ),
            "note": TextInput(
                attrs={
                    "class": "form-control w-full input input-bordered",
                    "placeholder": "請輸入您的備註",
                }
            ),
        }
        labels = {
            "hire_date": "入職時間",
            "note": "備註",
        }

        # 初始化方法，用於在表單實例化時做初始設定
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        # ----------這段目前看起來沒成功----------
        # clean_XXXX 方法可用來加強表單的驗證邏輯
        # UserCreationForm 預設已包含檢查兩次密碼是否一致，帳號是否已存在
        def clean_password2(self):
            password1 = self.cleaned_data.get("password1")
            password2 = self.cleaned_data.get("password2")

            # 檢查兩次密碼是否一致
            if password1 and password2 and password1 != password2:
                raise forms.ValidationError("兩次輸入的密碼不一致")

            # 檢查密碼長度和內容
            if len(password2) < 8:
                raise forms.ValidationError("密碼長度必須大於 8 個字符。")
            if not any(char.isdigit() for char in password2):
                raise forms.ValidationError("密碼必須包含至少一個數字。")
            if not any(char.isalpha() for char in password2):
                raise forms.ValidationError("密碼必須包含至少一個字母。")

            return password2

        def clean_email(self):
            email = self.cleaned_data.get("email")
            if CustomUser.objects.filter(email=email).exists():
                raise forms.ValidationError("Email already exists")
            return email

        def clean_username(self):
            username = self.cleaned_data.get("username")
            if len(username) < 10:
                raise forms.ValidationError("帳號長度必須大於 10 個字符。")
            return username
