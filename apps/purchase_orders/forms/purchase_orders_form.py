from django import forms

from ..models import PurchaseOrder  # Import the PurchaseOrder model


class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = [
            "order_number",
            "supplier",
            "supplier_tel",
            "contact_person",
            "supplier_email",
            "notes",
            "total_amount",
        ]
        widgets = {
            "total_amount": forms.NumberInput(attrs={"step": "0.1"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }
