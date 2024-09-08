import re  # Import the re module for regular expressions

from django import forms

from ..models import Supplier


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = [
            "name",
            "telephone",
            "contact_person",
            "email",
            "gui_number",
            "address",
            "note",
        ]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "placeholder": "Supplier Name",
                    "class": "w-full box-border",
                }
            ),
            "telephone": forms.TextInput(
                attrs={
                    "placeholder": "Telephone Number",
                    "class": "w-full box-border",
                }
            ),
            "contact_person": forms.TextInput(
                attrs={
                    "placeholder": "Contact Person",
                    "class": "w-full box-border",
                }
            ),
            "email": forms.TextInput(
                attrs={
                    "placeholder": "Email Address",
                    "class": "w-full box-border",
                }
            ),
            "address": forms.TextInput(
                attrs={
                    "placeholder": "Address",
                    "class": "w-full box-border",
                }
            ),
            "note": forms.Textarea(
                attrs={
                    "placeholder": "Additional Notes",
                    "rows": 3,
                    "class": "w-full box-border",
                }
            ),
        }
        labels = {
            "name": "Supplier Name",
            "telephone": "Telephone Number",
            "contact_person": "Contact Person",
            "email": "Email Address",
            "gui_number": "GUI Number",
            "address": "Address",
            "note": "Additional Notes",
        }
        help_texts = {
            "name": "Enter the full name of the supplier",
            "telephone": "Enter a phone number (e.g., 0912345678)",
            "contact_person": "Enter the name of the primary contact person",
            "email": "Enter a valid email (e.g., example@gmail.com)",
            "gui_number": "Enter an 8-digit GUI number (e.g., 12345678)",
            "address": "Enter the full address of the supplier",
            "note": "Any additional notes or comments",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get("name")
        telephone = cleaned_data.get("telephone")
        contact_person = cleaned_data.get("contact_person")
        email = cleaned_data.get("email")
        gui_number = cleaned_data.get("gui_number")
        address = cleaned_data.get("address")

        if not name:
            self.add_error("name", "Supplier Name is required.")

        if telephone == "":
            self.add_error("telephone", "Telephone is required.")
        elif not re.match(
            r"^(09\d{2}-\d{3}-\d{3}|09\d{8}|09\d{2}-\d{6}|0\d{8}|0\d-\d{7}|0\d-\d{3}-\d{4}|0\d-\d{4}-\d{3})$",
            telephone,
        ):
            self.add_error("telephone", "Invalid phone number.")

        if not contact_person:
            self.add_error("contact_person", "Contact Person is required.")

        if email == "":
            self.add_error("email", "Email address is required.")

        if gui_number == "":
            self.add_error("gui_number", "GUI Number is required.")
        elif not re.match(r"^\d{8}$", gui_number):
            self.add_error("gui_number", "Invalid GUI number.")

        if not address:
            self.add_error("address", "Address is required.")

        return cleaned_data
