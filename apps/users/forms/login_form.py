from django import forms
from django.contrib.auth import authenticate

from apps.users.models import CustomUser


class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control w-full input input-bordered",
                "placeholder": "請輸入您的帳號",
            }
        ),
        label="帳號",
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control w-full input input-bordered",
                "placeholder": "請輸入您的密碼",
            }
        ),
        required=False,
        label="密碼",
    )

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if username == "":
            self.add_error("username", "請輸入您的帳號")
        elif not CustomUser.objects.filter(username=username).exists():
            self.add_error("username", "此帳號不存在")
        return username

    def clean_password(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")

        user = authenticate(username=username, password=password)

        if username:
            if password and user is None:
                raise forms.ValidationError("您的密碼輸入錯誤")
            elif not password:
                raise forms.ValidationError("請輸入您的密碼")

        return password
