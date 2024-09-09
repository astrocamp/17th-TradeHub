from django import forms

from ..models import SalesOrder


class SalesOrderForm(forms.ModelForm):
    class Meta:
        model = SalesOrder
        fields = [
            "client",
            "product",
            "quantity",
            "stock",
            "price",
        ]
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
        }
        help_texts = {
            "client": "Please select a client.",
            "product": "Please select a product.",
            "quantity": "Please enter the quantity.",
            "stock": "Please select a stock.",
            "price": "Please enter the price.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False

    def clean(self):
        cleaned_data = super().clean()
        client = cleaned_data.get("client")
        product = cleaned_data.get("product")
        quantity = cleaned_data.get("quantity")
        stock = cleaned_data.get("stock")
        price = cleaned_data.get("price")

        if not client:
            self.add_error("client", "Client is required.")

        if not product:
            self.add_error("product", "Product is required.")

        if quantity is None:
            self.add_error("quantity", "Quantity is required.")
        elif quantity == 0:
            self.add_error("quantity", "Quantity should not be zero.")

        if not stock:
            self.add_error("stock", "Stock is required.")

        if price is None:
            self.add_error("price", "Price is required.")
        elif price == 0:
            self.add_error("price", "Price should not be zero.")

        return cleaned_data
