from django import forms
from django.forms import ModelForm

from apps.products.models import Product


class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = [
            "product_id",
            "product_name",
            "price",
            "supplier",
            "note",
        ]
        widgets = {
            "product_id": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Product ID"}
            ),
            "product_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Product Name"}
            ),
            "price": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Price"}
            ),
            "supplier": forms.Select(
                attrs={
                    "class": "form-control w-full select select-bordered flex items-center justify-center"
                }
            ),
            "note": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Additional Note",
                    "rows": 3,
                }
            ),
        }
        labels = {
            "product_id": "Product ID",
            "product_name": "Product Name",
            "price": "Price",
            "supplier": "Supplier",
            "note": "Additional Notes",
        }
        help_texts = {
            "product_id": "Please enter the product ID.",
            "product_name": "Please enter the full name of the product.",
            "price": "Please enter the product price.",
            "supplier": "Please select the supplier from the list.",
            "note": "You can enter any additional notes or comments here.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False

    def clean(self):
        cleaned_data = super().clean()
        product_id = cleaned_data.get("product_id")
        product_name = cleaned_data.get("product_name")
        price = cleaned_data.get("price")

        if not product_id:
            self.add_error("product_id", "Product ID is required.")

        if not product_name:
            self.add_error("product_name", "Product Name is required.")
            
        if not price:
            self.add_error("price", "Price is required.")
        else:
            if price < 0:
                self.add_error("price", "Price cannot be negative.")

        return cleaned_data
