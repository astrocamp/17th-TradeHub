from django import forms

from ..models import Inventory


class RestockForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = ["product", "supplier", "quantity", "safety_stock", "note"]

        widgets = {
            "product": forms.TextInput(
                attrs={"class": "form-control input input-bordered w-full"}
            ),
            "supplier": forms.TextInput(
                attrs={"class": "form-control input input-bordered w-full"}
            ),
            "quantity": forms.NumberInput(
                attrs={"class": "form-control input input-bordered w-full"}
            ),
            "safety_stock": forms.NumberInput(
                attrs={"class": "form-control input input-bordered w-full"}
            ),
            "note": forms.TextInput(
                attrs={"class": "form-control input input-bordered w-full"}
            ),
            "last_updated": forms.DateTimeInput(attrs={"class": "form-control"}),
        }
