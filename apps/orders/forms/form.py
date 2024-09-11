from django import forms

from ..models import Orders


class OrderForm(forms.ModelForm):
    class Meta:
        model = Orders
        fields = "__all__"

        widgets = {
            "code": forms.TextInput(attrs={"class": "form-control"}),
            "client_fk": forms.Select(attrs={"class": "form-control"}),
            "product_fk": forms.Select(attrs={"class": "form-control"}),
            "note": forms.Textarea(attrs={"class": "form-control"}),
        }
