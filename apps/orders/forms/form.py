from django import forms
from ..models import Orders


class OrderForm(forms.ModelForm):
    class Meta:
        module = Orders
        fields = "__all__"

        widgets = {
            "code": forms.TextInput(attrs={"class": "form-control"}),
            "client": forms.TextInput(attrs={"class": "form-control"}),
            "product": forms.TextInput(attrs={"class": "form-control"}),
            "note": forms.Textarea(attrs={"class": "form-control"}),
        }
