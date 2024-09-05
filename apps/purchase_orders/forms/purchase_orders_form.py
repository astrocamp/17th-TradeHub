from django import forms

from ..models import PurchaseOrder  # Import the PurchaseOrder model


class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = [
            "order_number",
            "supplier",
            "order_date",
            "total_amount",
            "notes",
        ]
        widgets = {
            "order_date": forms.DateInput(attrs={"type": "date"}),
            "total_amount": forms.NumberInput(attrs={"step": "0.01"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False

    def clean(self):
        cleaned_data = super().clean()
        order_number = cleaned_data.get("order_number")
        supplier = cleaned_data.get("supplier")
        order_date = cleaned_data.get("order_date")
        total_amount = cleaned_data.get("total_amount")

        if not order_number:
            self.add_error("order_number", "Order Number is required.")
        if not supplier:
            self.add_error("supplier", "Supplier is required.")
        if not order_date:
            self.add_error("order_date", "Order Date is required.")
        if not total_amount:
            self.add_error("total_amount", "Total Amount is required.")
        else:
            if total_amount <= 0:
                self.add_error("total_amount", "Total Amount must be greater than 0.")

        return cleaned_data
