from django import forms
from django.forms import inlineformset_factory

from ..models import ProductItem, PurchaseOrder


class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = [
            "supplier",
            "supplier_tel",
            "contact_person",
            "supplier_email",
            "notes",
            "total_amount",
        ]
        widgets = {
            "order_number": forms.TextInput(attrs={"readonly": "readonly"}),
            "supplier": forms.Select(attrs={"class": "w-full"}),
            "supplier_tel": forms.TextInput(attrs={"class": "w-full"}),
            "contact_person": forms.TextInput(attrs={"class": "w-full"}),
            "supplier_email": forms.TextInput(attrs={"class": "w-full"}),
            "total_amount": forms.NumberInput(attrs={"class": "w-full"}),
            "notes": forms.Textarea(attrs={"rows": 2, "class": "w-full"}),
        }


class ProductItemForm(forms.ModelForm):
    class Meta:
        model = ProductItem
        fields = ["product", "quantity", "price", "subtotal"]
        widgets = {
            "product": forms.Select(attrs={"class": "w-full"}),
            "quantity": forms.NumberInput(attrs={"class": "w-full", "min": 1}),
            "price": forms.NumberInput(attrs={"class": "w-full"}),
            "subtotal": forms.NumberInput(attrs={"class": "w-full"}),
        }


ProductItemFormSet = inlineformset_factory(
    PurchaseOrder, ProductItem, form=ProductItemForm, extra=1, can_delete=True
)
