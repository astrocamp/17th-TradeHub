import re

from django import forms

from apps.clients.models import Client


class FileUploadForm(forms.Form):
    file = forms.FileField()


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = [
            "name",
            "phone_number",
            "address",
            "email",
            "note",
        ]

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control w-full rounded-md p-2 bg-gray-100",
                    "placeholder": "請輸入客戶的全名",
                }
            ),
            "phone_number": forms.TextInput(
                attrs={
                    "class": "form-control w-full rounded-md p-2 bg-gray-100",
                    "placeholder": "請輸入客戶的電話號碼",
                }
            ),
            "address": forms.TextInput(
                attrs={
                    "class": "form-control w-full rounded-md p-2 bg-gray-100",
                    "placeholder": "請輸入客戶的地址",
                }
            ),
            "email": forms.TextInput(
                attrs={
                    "class": "form-control w-full rounded-md p-2 bg-gray-100",
                    "placeholder": "請輸入客戶的電子信箱",
                }
            ),
            "note": forms.Textarea(
                attrs={
                    "class": "form-control w-full rounded-md p-2 bg-gray-100 text-sm",
                    "placeholder": "如有其他備註事項，請填入",
                    "rows": 3,
                }
            ),
        }
        labels = {
            "name": "客戶名稱",
            "phone_number": "電話號碼",
            "address": "地址",
            "email": "電子信箱",
            "note": "備註",
        }
        help_texts = {
            "name": "例: 五倍貿易",
            "phone_number": "例: 行動電話:0912345678 / 市話:02-28345678",
            "address": "例: 台北市中正區衡陽路123號",
            "email": "例: 5xcampus@gmail.com",
            "note": "例: 備用電話 / 備註事項",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get("name")
        phone_number = cleaned_data.get("phone_number")
        address = cleaned_data.get("address")
        email = cleaned_data.get("email")

        if not name:
            self.add_error("name", "請填入客戶全名")

        if phone_number == "":
            self.add_error("phone_number", "請填入電話號碼")
        elif not re.match(
            r"^(09\d{2}-\d{3}-\d{3}|09\d{8}|09\d{2}-\d{6}|0(37|49)\d{7}|0(37|49)-\d{7}|0(37|49)-\d{3}-\d{4}|0(37|49)-\d{4}-\d{3}|0\d{8}|0\d{9}|0\d-\d{7}|0\d-\d{8}|0\d-\d{3}-\d{4}|0\d-\d{4}-\d{3}|0\d-\d{4}-\d{4})$",
            phone_number,
        ):
            self.add_error("phone_number", "請填入正確的電話號碼")

        if email == "":
            self.add_error("email", "請填入電子信箱")
        elif Client.objects.filter(email=email).exclude(id=self.instance.id).exists():
            self.add_error("email", "此電子信箱已被使用")

        if not address:
            self.add_error("address", "請填入地址")

        return cleaned_data
