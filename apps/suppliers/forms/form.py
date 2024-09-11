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
            "name": forms.TextInput(attrs={"placeholder": "Supplier Name"}),
            "telephone": forms.TextInput(attrs={"placeholder": "Telephone Number"}),
            "contact_person": forms.TextInput(attrs={"placeholder": "Contact Person"}),
            "email": forms.TextInput(attrs={"placeholder": "Email Address"}),
            "gui_number": forms.TextInput(attrs={"placeholder": "GUI Number"}),
            "address": forms.TextInput(
                attrs={
                    "placeholder": "Address",
                    "rows": 4,
                    "class": "w-full box-border",
                }
            ),
            "note": forms.Textarea(
                attrs={
                    "placeholder": "Additional Notes",
                    "rows": 4,
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
        super(SupplierForm, self).__init__(*args, **kwargs)
        # Remove the required attribute from all fields
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

        # Validate 'name'
        if not name:
            self.add_error("name", "This field cannot be empty.")

        # Validate 'telephone'
        if not telephone:
            self.add_error("telephone", "This field cannot be empty.")
        elif not re.match(r"^09\d{8}$", telephone):
            self.add_error("telephone", "Invalid phone number.")

        # Validate 'contact_person'
        if not contact_person:
            self.add_error("contact_person", "This field cannot be empty.")

        # Validate 'email'
        if not email:
            self.add_error("email", "This field cannot be empty.")
        elif not re.match(r"^[\w.-]+@[\w.-]+\.\w{2,}$", email):
            self.add_error("email", "Invalid email address.")

        # Validate 'gui_number'
        if not gui_number:
            self.add_error("gui_number", "This field cannot be empty.")
        elif not re.match(r"^\d{8}$", gui_number):
            self.add_error("gui_number", "Invalid GUI number.")

        # Validate 'address'
        if not address:
            self.add_error("address", "This field cannot be empty.")

        return cleaned_data
