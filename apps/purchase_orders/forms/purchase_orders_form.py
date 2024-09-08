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
            "total_amount": forms.NumberInput(attrs={"class": "w-full"}),
            "notes": forms.Textarea(attrs={"rows": 3, "class": "w-full"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False

    def clean(self):
        cleaned_data = super().clean()
        order_number = cleaned_data.get("order_number")
        supplier = cleaned_data.get("supplier")
        supplier_tel = cleaned_data.get("supplier_tel")
        contact_person = cleaned_data.get("contact_person")
        supplier_email = cleaned_data.get("supplier_email")
        notes = cleaned_data.get("notes")
        total_amount = cleaned_data.get("total_amount")

        if not order_number:
            self.add_error("order_number", "Order Number is required.")
        if not supplier:
            self.add_error("supplier", "Supplier is required.")
        if not supplier_tel:
            self.add_error("supplier_tel", "Supplier Tel is required.")
        if not contact_person:
            self.add_error("contact_person", "Contact Person is required.")
        if not supplier_email:
            self.add_error("supplier_email", "Supplier Email is required.")
        if not total_amount:
            self.add_error("total_amount", "Total Amount is required.")
        else:
            if total_amount <= 0:
                self.add_error("total_amount", "Total Amount must be greater than 0.")

        return cleaned_data
