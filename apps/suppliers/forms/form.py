import re  # Import the re module for regular expressions

from django import forms

from ..models import Supplier


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = [
            "name",
            "telephone",
            "contact_person",
            "email",
            "gui_number",
            "address",
            "note",
        ]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "placeholder": "請輸入供應商名稱",
                    "class": "form-control w-full rounded-md p-2 bg-gray-100",
                }
            ),
            "telephone": forms.TextInput(
                attrs={
                    "placeholder": "請輸入供應商的電話號碼",
                    "class": "form-control w-full rounded-md p-2 bg-gray-100",
                }
            ),
            "contact_person": forms.TextInput(
                attrs={
                    "placeholder": "請輸入聯絡人名稱",
                    "class": "form-control w-full rounded-md p-2 bg-gray-100",
                }
            ),
            "email": forms.TextInput(
                attrs={
                    "placeholder": "請輸入供應商的電子信箱",
                    "class": "form-control w-full rounded-md p-2 bg-gray-100",
                }
            ),
            "gui_number": forms.TextInput(
                attrs={
                    "placeholder": "請輸入統一編號",
                    "class": "form-control w-full rounded-md p-2 bg-gray-100",
                }
            ),
            "address": forms.TextInput(
                attrs={
                    "placeholder": "請輸入供應商的地址",
                    "class": "form-control w-full rounded-md p-2 bg-gray-100",
                }
            ),
            "note": forms.Textarea(
                attrs={
                    "placeholder": "如有其他備註事項，請填入",
                    "rows": 3,
                    "class": "form-control w-full rounded-md p-2 bg-gray-100 text-sm",
                }
            ),
        }
        labels = {
            "name": "供應商名稱",
            "telephone": "電話號碼",
            "contact_person": "聯絡人",
            "email": "電子信箱",
            "gui_number": "統一編號",
            "address": "地址",
            "note": "備註",
        }
        help_texts = {
            "name": "例: 五倍貿易(請填入公司全名)",
            "telephone": "例: 行動電話:0912345678 / 市話:02-28345678",
            "contact_person": "例: 王小明",
            "email": "例: 5xcampus@gmail.com",
            "gui_number": "例: 10458574(請填入正確的統一編號)",
            "address": "例: 台北市中正區衡陽路123號",
            "note": "例: 備用電話 / 備註事項",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get("name")
        telephone = cleaned_data.get("telephone")
        contact_person = cleaned_data.get("contact_person")
        email = cleaned_data.get("email")
        address = cleaned_data.get("address")

        if not name:
            self.add_error("name", "請填入供應商名稱")

        if telephone == "":
            self.add_error("telephone", "請填入電話號碼")
        elif not re.match(
            r"^(09\d{2}-\d{3}-\d{3}|09\d{8}|09\d{2}-\d{6}|0(37|49)\d{7}|0(37|49)-\d{7}|0(37|49)-\d{3}-\d{4}|0(37|49)-\d{4}-\d{3}|0\d{8}|0\d{9}|0\d-\d{7}|0\d-\d{8}|0\d-\d{3}-\d{4}|0\d-\d{4}-\d{3}|0\d-\d{4}-\d{4})$",
            telephone,
        ):
            self.add_error("telephone", "請填入正確的電話號碼")

        if not contact_person:
            self.add_error("contact_person", "請填入聯絡人姓名")

        if email == "":
            self.add_error("email", "請填入電子信箱")
        elif Supplier.objects.filter(email=email).exclude(id=self.instance.id).exists():
            self.add_error("email", "此電子信箱已被使用")

        if not address:
            self.add_error("address", "請填入地址")

        return cleaned_data

    def clean_gui_number(self):
        gui_number = self.cleaned_data.get("gui_number")
        if gui_number == "":
            self.add_error("gui_number", "請填入統一編號")
        else:
            try:
                # 驗證統一編號
                validation_message = self.validate_gui_number(gui_number)
                if validation_message != "統編驗證成功":
                    self.add_error("gui_number", validation_message)
            except ValueError as e:
                self.add_error("gui_number", str(e))
            except Exception:
                self.add_error("gui_number", "統編驗證失敗")

        return gui_number

    def validate_gui_number(self, gui_number):
        logic_multipliers = [1, 2, 1, 2, 1, 2, 4, 1]
        logic_sum = 0

        for i in range(8):
            product = int(gui_number[i]) * logic_multipliers[i]
            logic_sum += sum(int(digit) for digit in str(product))

        if gui_number[6] == "7":
            if logic_sum % 5 == 0 or (logic_sum + 1) % 5 == 0:
                return "統編驗證成功"
        else:
            if logic_sum % 5 == 0:
                return "統編驗證成功"
        return "統編驗證失敗"
