import re

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
                attrs={
                    "class": "w-full form-control px-2 py-1 focus:outline-none cursor-not-allowed",
                    "readonly": "readonly",
                },
            ),
            "hire_date": forms.DateInput(
                attrs={
                    "class": "w-full form-control px-2 py-1 focus:outline-none cursor-not-allowed",
                    "type": "date",
                    "readonly": "readonly",
                }
            ),
            "username": forms.TextInput(
                attrs={
                    "class": "w-full form-control px-2 py-1 focus:outline-none cursor-not-allowed",
                    "readonly": "readonly",
                }
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

    def clean(self):
        cleaned_data = super().clean()
        first_name = cleaned_data.get("first_name")
        phone = cleaned_data.get("phone")
        birthday = cleaned_data.get("birthday")

        if not first_name:
            self.add_error("first_name", "姓名為必填欄位")
        if not phone:
            self.add_error("phone", "電話號碼為必填欄位")
        elif not re.match(
            r"^(09\d{2}-\d{3}-\d{3}|09\d{8}|09\d{2}-\d{6}|0(37|49)\d{7}|0(37|49)-\d{7}|0(37|49)-\d{3}-\d{4}|0(37|49)-\d{4}-\d{3}|0\d{8}|0\d{9}|0\d-\d{7}|0\d-\d{8}|0\d-\d{3}-\d{4}|0\d-\d{4}-\d{3}|0\d-\d{4}-\d{4})$",
            phone,
        ):
            self.add_error("phone", "請填入正確的電話號碼")
        if not birthday:
            self.add_error("birthday", "生日為必填欄位")

        return cleaned_data
