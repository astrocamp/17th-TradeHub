from django import forms
from django.core.validators import MinLengthValidator, RegexValidator

from apps.users.models import CustomUser, Invitation


class InvitationRegistrationForm(forms.ModelForm):
    token = forms.CharField(max_length=50, required=True)
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

    class Meta:
        model = CustomUser
        fields = [
            "username",
            "password1",
            "password2",
            "email",
            "token",
        ]

    def clean_token(self):
        token = self.cleaned_data["token"]
        try:
            invitation = Invitation.objects.get(token=token, is_used=False)
        except Invitation.DoesNotExist:
            raise forms.ValidationError("無效邀請碼")
        self.cleaned_data["company"] = invitation.company
        return token

    def save(self, commit=True):
        user = super().save(commit=False)
        user.company = self.cleaned_data["company"]
        if commit:
            user.save()
            Invitation.objects.filter(token=self.cleaned_data["token"]).update(
                is_used=True
            )
        return user
