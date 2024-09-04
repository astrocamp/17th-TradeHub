from django import forms

from ..models import SalesOrder


class SalesOrderForm(forms.ModelForm):
    class Meta:
        model = SalesOrder
        fields = ["client", "product", "quantity", "stock", "price"]
        widgets = {
            "client": forms.Select(
                attrs={
                    "class": "form-control w-full select select-bordered flex items-center justify-center"
                }
            ),
            "product": forms.Select(
                attrs={
                    "class": "form-control w-full select select-bordered flex items-center justify-center"
                }
            ),
            "quantity": forms.NumberInput(
                attrs={
                    "class": "form-control w-full input input-bordered flex items-center justify-center"
                }
            ),
            "stock": forms.Select(
                attrs={
                    "class": "form-control w-full select select-bordered flex items-center justify-center"
                }
            ),
            "price": forms.NumberInput(
                attrs={
                    "class": "form-control w-full input input-bordered flex items-center justify-center"
                }
            ),
            # "created_at": forms.DateTimeInput(
            #     attrs={
            #         "class": "form-control w-full input input-bordered flex items-center justify-center"
            #     }
            # ),
            # "updated_at": forms.DateTimeInput(
            #     attrs={
            #         "class": "form-control w-full input input-bordered flex items-center justify-center"
            #     }
            # ),
        }
