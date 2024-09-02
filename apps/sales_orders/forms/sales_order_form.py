from django import forms

from ..models import SalesOrder


class SalesOrderForm(forms.ModelForm):
    class Meta:
        model = SalesOrder
        fields = "__all__"
        widgets = {
            "client": forms.Select(
                attrs={
                    "class": "form-control w-full select select-bordered flex items-center justify-center"
                }
            ),
            "products": forms.Select(
                attrs={
                    "class": "form-control w-full select select-bordered flex items-center justify-center"
                }
            ),
            "quantity": forms.TextInput(
                attrs={
                    "class": "form-control w-full input input-bordered flex items-center justify-center"
                }
            ),
            "stock": forms.Select(
                attrs={
                    "class": "form-control w-full select select-bordered flex items-center justify-center"
                }
            ),
            "price": forms.TextInput(
                attrs={
                    "class": "form-control w-full input input-bordered flex items-center justify-center"
                }
            ),
            "created_at": forms.DateTimeInput(
                attrs={
                    "class": "form-control w-full input input-bordered flex items-center justify-center"
                }
            ),
            "updated_at": forms.DateTimeInput(
                attrs={
                    "class": "form-control w-full input input-bordered flex items-center justify-center"
                }
            ),
        }
