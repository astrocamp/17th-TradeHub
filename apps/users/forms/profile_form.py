from django import forms

from ..models import CustomUser


class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            "first_name",
            "last_name",
            "department",
            "position",
            "email",
            "hire_date",
            "username",
            "birthday",
            "phone",
            "address",
            "note",
        ]
        widgets = {
            "first_name": forms.TextInput(
                attrs={
                    "class": "w-full form-control border px-2 py-1",
                    "placeholder": "名",
                }
            ),
            "last_name": forms.TextInput(
                attrs={
                    "class": "w-full form-control border px-2 py-1",
                    "placeholder": "姓",
                }
            ),
            "department": forms.Select(
                attrs={"class": "w-full form-control border px-2 py-1"}
            ),
            "position": forms.Select(
                attrs={"class": "w-full form-control border px-2 py-1"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "w-full form-control border px-2 py-1"}
            ),
            "hire_date": forms.DateInput(
                attrs={
                    "class": "w-full form-control border px-2 py-1",
                    "type": "date",
                    "readonly": "readonly",
                }
            ),
            "username": forms.TextInput(
                attrs={"class": "w-full form-control border px-2 py-1"}
            ),
            "birthday": forms.DateInput(
                attrs={
                    "class": "w-full form-control border px-2 py-1",
                    "type": "date",
                }
            ),
            "phone": forms.TextInput(
                attrs={"class": "w-full form-control border px-2 py-1"}
            ),
            "address": forms.TextInput(
                attrs={"class": "w-full form-control border px-2 py-1"}
            ),
            "note": forms.TextInput(
                attrs={"class": "w-full form-control border px-2 py-1"}
            ),
        }
        labels = {
            "first_name": "姓名",
            "department": "部門",
            "position": "職位",
            "email": "Email",
            "hire_date": "入職日期",
            "username": "帳號",
            "birthday": "生日",
            "phone": "電話",
            "address": "地址",
            "note": "備註",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False
