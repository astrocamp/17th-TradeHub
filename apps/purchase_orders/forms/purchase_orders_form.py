from django import forms
from django.forms import inlineformset_factory

from ..models import PurchaseOrder, PurchaseOrderProduct


class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = [
            "supplier",
            "supplier_tel",
            "contact_person",
            "supplier_email",
            "notes",
            "total_amount",
        ]
        widgets = {
            "order_number": forms.TextInput(attrs={"readonly": "readonly"}),
            "supplier": forms.Select(attrs={"class": "w-full"}),
            "supplier_tel": forms.TextInput(attrs={"class": "w-full"}),
            "contact_person": forms.TextInput(attrs={"class": "w-full"}),
            "supplier_email": forms.TextInput(attrs={"class": "w-full"}),
            "total_amount": forms.NumberInput(attrs={"class": "w-full"}),
            "notes": forms.Textarea(attrs={"rows": 2, "class": "w-full"}),
        }


class PurchaseOrderProductForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrderProduct
        fields = ["product", "quantity"]


# 管理主模型跟子模型(中介模型)的多對多關係
PurchaseOrderProductFormSet = inlineformset_factory(
    PurchaseOrder,
    PurchaseOrderProduct,
    form=PurchaseOrderProductForm,
    extra=1,
    can_delete=True,
)
