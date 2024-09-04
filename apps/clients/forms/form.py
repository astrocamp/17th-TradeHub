from django import forms
import re

from ..models import Client


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ["name", "phone_number", "address", "email", "note"]

        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Client Name"}),
            "phone_number": forms.TextInput(attrs={"class": "form-control", "placeholder": "Phone Number"}),
            "address": forms.TextInput(attrs={"class": "form-control", "placeholder": "Address"}),
            "email": forms.TextInput(attrs={"class": "form-control", "placeholder": "Email Address"}),
            "note": forms.Textarea(attrs={"class": "form-control", "placeholder": "Additional Notes", "rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super(ClientForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get("name")
        phone_number = cleaned_data.get("phone_number")
        address = cleaned_data.get("address")
        email = cleaned_data.get("email")

        if not name:
            self.add_error("name", "Client name is required")

        if not phone_number:
            self.add_error("phone_number", "Phone number is required")
        elif not re.match(r"^09\d{8}$", phone_number):
            self.add_error("phone_number", "Invalid phone number.")

        if not email:
            self.add_error("email", "Email address is required")
        elif not re.match(r"^[\w.-]+@[\w.-]+\.\w{2,}$", email):
            self.add_error("email", "Invalid email address.")

        if not address:
            self.add_error("address", "Address is required")

        return cleaned_data
