from django.forms import ModelForm
from django.forms.widgets import TextInput

from apps.company.models import Company


class CompanyForm(ModelForm):
    class Meta:
        model = Company
        fields = ["company_name", "gui_number", "address", "contact_person"]
        widgets = {
            "company_name": TextInput(attrs={"class": "form-control"}),
            "gui_number": TextInput(attrs={"class": "form-control"}),
            "address": TextInput(attrs={"class": "form-control"}),
            "contact_person": TextInput(attrs={"class": "form-control"}),
        }
        labels = {
            "company_name": "公司名稱",
            "gui_number": "統一編號",
            "address": "地址",
            "contact_person": "聯絡人",
        }
