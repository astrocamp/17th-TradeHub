from django import forms

from ..models import Orders


class OrderForm(forms.ModelForm):
    class Meta:
        model = Orders
        fields = "__all__"

        widgets = {
            "code": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Order Code"}
            ),
            "client_fk": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
            "product_fk": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
            "note": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Any additional notes",
                    "rows": 3,
                }
            ),
        }
        help_texts = {
            "code": "Please enter the order code.",
            "client_fk": "Please select a client.",
            "product_fk": "Please select a product.",
            "note": "Please enter any additional notes.",
        }

        labels = {
            "code": "Order Code",
            "client_fk": "Client",
            "product_fk": "Product",
            "note": "Note",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False

    def clean(self):
        cleaned_data = super().clean()
        code = cleaned_data.get("code")
        client_fk = cleaned_data.get("client_fk")
        product_fk = cleaned_data.get("product_fk")

        if not code:
            self.add_error("code", "Order code is required.")

        if not client_fk:
            self.add_error("client_fk", "Client is required.")

        if not product_fk:
            self.add_error("product_fk", "Product is required.")

        return cleaned_data
