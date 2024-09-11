from django import forms

from ..models import Inventory


class RestockForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = [
            "product",
            "supplier",
            "quantity",
            "safety_stock",
            "note",
        ]

        widgets = {
            "product": forms.Select(
                attrs={
                    "class": "form-control w-full select select-bordered flex items-center justify-center",
                    "readonly": "readonly",
                }
            ),
            "supplier": forms.Select(
                attrs={
                    "class": "form-control w-full select select-bordered flex items-center justify-center",
                    "readonly": "readonly",
                }
            ),
            "quantity": forms.NumberInput(
                attrs={"class": "form-control input input-bordered w-full"}
            ),
            "safety_stock": forms.NumberInput(
                attrs={"class": "form-control input input-bordered w-full"}
            ),
            "note": forms.Textarea(
                attrs={
                    "class": "form-control input input-bordered w-full",
                    "placeholder": "Any additional notes",
                    "rows": 3,
                }
            ),
        }
        help_texts = {
            "product": "Please select the product.",
            "supplier": "Please select the supplier.",
            "quantity": "Please enter the quantity of the product.",
            "safety_stock": "Please enter the safety stock of the product.",
            "note": "Please enter any additional notes about the product.",
        }
        labels = {
            "product": "Product",
            "supplier": "Supplier",
            "quantity": "Quantity",
            "safety_stock": "Safety Stock",
            "note": "Note",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False

    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get("product")
        supplier = cleaned_data.get("supplier")
        quantity = cleaned_data.get("quantity")
        safety_stock = cleaned_data.get("safety_stock")

        if not product:
            self.add_error("product", "Product is required.")

        if not supplier:
            self.add_error("supplier", "Supplier is required.")

        if quantity is None:
            self.add_error("quantity", "Quantity is required.")

        if safety_stock is None:
            self.add_error("safety_stock", "Safety stock is required.")

        return cleaned_data
