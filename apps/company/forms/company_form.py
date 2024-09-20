from django.forms import ModelForm

from apps.company.models import Company


class CompanyForm(ModelForm):
    class Meta:
        model = Company
        fields = ["company_id", "company_name", "gui_number", "address", "user"]
