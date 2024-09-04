from django import forms

from ..models import PurchaseOrder  # Import the PurchaseOrder model


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
            "total_amount": forms.NumberInput(attrs={"step": "0.1"}),
            "notes": forms.Textarea(attrs={"rows": 2, "class": "w-full"}),
        }
