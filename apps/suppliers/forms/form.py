from django.forms import ModelForm

from ..models import Supplier


class SupplierForm(ModelForm):
    class Meta:
        model = Supplier
        fields = ["name", "tel", "contact","GUInumber","address", "remark"]
