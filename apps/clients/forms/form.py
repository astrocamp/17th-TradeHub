import re

from django import forms

from ..models import Client


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = [
            "name",
            "phone_number",
            "address",
            "email",
            "note",
        ]

        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Client Name"}
            ),
            "phone_number": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Phone Number"}
            ),
            "address": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Address"}
            ),
            "email": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Email Address"}
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
            "name": "Enter full name of client.",
            "phone_number": "Enter phone number of client (e.g., 0912345678 or 02-28345678).",
            "address": "Enter address of client.",
            "email": "Enter email address of client.",
            "note": "Enter any additional notes of client.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get("name")
        phone_number = cleaned_data.get("phone_number")
        address = cleaned_data.get("address")
        email = cleaned_data.get("email")

        if not name:
            self.add_error("name", "Client name is required.")

        if phone_number == "":
            self.add_error("phone_number", "Phone number is required.")
        elif not re.match(
            r"^(09\d{2}-\d{3}-\d{3}|09\d{8}|0\d{8}|0\d-\d{7}|0\d-\d{3}-\d{4}|0\d-\d{4}-\d{3})$",
            phone_number,
        ):
            self.add_error("phone_number", "Invalid phone number.")

        if email == "":
            self.add_error("email", "Email address is required.")

        if not address:
            self.add_error("address", "Address is required.")

        return cleaned_data
