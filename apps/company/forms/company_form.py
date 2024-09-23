from django.forms import ModelForm
from django.forms.widgets import TextInput

from apps.company.models import Company


class CompanyForm(ModelForm):
    class Meta:
        model = Company
        fields = ["company_name", "gui_number", "address", "contact_person"]
        widgets = {
            "company_name": TextInput(
                attrs={
                    "class": "form-control w-full rounded-md p-2 bg-gray-100",
                    "placeholder": "請輸入公司名稱",
            }),
            "gui_number": TextInput(
                attrs={
                    "class": "form-control w-full rounded-md p-2 bg-gray-100",
                    "placeholder": "請輸入統一編號",
                }
            ),
            "address": TextInput(
                attrs={
                    "class": "form-control w-full rounded-md p-2 bg-gray-100",
                    "placeholder": "請輸入地址",
                }
            ),
            "contact_person": TextInput(
                attrs={
                    "class": "form-control w-full rounded-md p-2 bg-gray-100",
                    "placeholder": "請輸入聯絡人",
                }
            ),
        }
        labels = {
            "company_name": "公司名稱",
            "gui_number": "統一編號",
            "address": "地址",
            "contact_person": "聯絡人",
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['contact_person'].initial = user.username
        for field in self.fields.values():
            field.required = False


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
    
    def clean_company_name(self):
        company_name = self.cleaned_data.get("company_name")
        if company_name == "":
            self.add_error("company_name", "請填入公司名稱")
        return company_name