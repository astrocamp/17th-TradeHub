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
                "placeholder": "Please enter your password.",
            }
        ),
        validators=[
            MinLengthValidator(
                8, message="Password must be at least 8 characters long."
            ),
            RegexValidator(
                regex=r"^[A-Za-z0-9]+$",
                message="Password must contain at least one number and one letter.",
            ),
        ],
        label="Password",
        help_text="Password must be at least 8 characters long, and cannot be entirely numeric or letters.",
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control w-full input input-bordered",
                "placeholder": "Please confirm your password again.",
            }
        ),
        label="Confirm Password",
        help_text="The passwords must match, its for confirmation.",
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
                    "placeholder": "Please enter your username.",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control w-full input input-bordered",
                    "placeholder": "purchasing@tradehub.com",
                }
            ),
        }
        labels = {
            "username": "Username",
            "email": "Email",
        }
        help_texts = {
            "username": "Username must be at least 6 characters long.",
            "password1": "Password must be at least 8 characters long, and cannot be entirely numeric.",
            "password2": "The passwords must match.",
            "email": "Must be in a valid email format.",
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
            raise forms.ValidationError("Username is required.")
        elif CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists.")
        elif len(username) < 6:
            raise forms.ValidationError("Username must be at least 6 characters long.")
        return username

    def clean_password1(self):
        password1 = self.cleaned_data.get("password1")

        if password1 == "":
            raise forms.ValidationError("Password is required.")
        elif len(password1) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        elif password1.isdigit() or password1.isalpha():
            raise forms.ValidationError(
                "Password cannot be entirely numeric or letters."
            )

        return password1

    def clean_password2(self):
        password2 = self.cleaned_data.get("password2")

        if password2 == "":
            raise forms.ValidationError("Please confirm your password again.")

        return password2

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email == "":
            raise forms.ValidationError("Email address is required.")
        elif CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Email address already exists.")
        return email
