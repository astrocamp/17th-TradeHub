from django import forms
from .models import Inventory


class RestockForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = ["product", "supplier", "quantity"]

        widgets = {
            "product": forms.Select(attrs={"class": "form-control"}),
            "supplier": forms.Select(attrs={"class": "form-control"}),
            "quantity": forms.NumberInput(attrs={"class": "form-control"}),
        }
