from django import forms

from ..models import Inventory


class RestockForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = ["product", "supplier", "quantity", "safety_stock", "note"]

        widgets = {
            "product": forms.Select(
                attrs={
                    "class": "form-control w-full select select-bordered flex items-center justify-center"
                }
            ),
            "supplier": forms.Select(
                attrs={
                    "class": "form-control w-full select select-bordered flex items-center justify-center"
                }
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
