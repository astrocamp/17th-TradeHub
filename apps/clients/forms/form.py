from django import forms

from ..models import Client


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ["name", "phone_number", "address", "email", "note"]

        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "phone_number": forms.TextInput(attrs={"class": "form-control"}),
            "address": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "note": forms.Textarea(attrs={"class": "form-control"}),
        }
