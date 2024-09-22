import re

from django import forms
from django.forms import inlineformset_factory

from apps.purchase_orders.models import ProductItem, PurchaseOrder


class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = [
            "supplier",
            "supplier_tel",
            "contact_person",
            "supplier_email",
            "amount",
            "note",
        ]
        labels = {
            "supplier": "供應商名稱",
            "supplier_tel": "供應商電話",
            "contact_person": "聯絡人",
            "supplier_email": "供應商Email",
            "amount": "總金額",
            "note": "備註",
        }
        widgets = {
            "supplier": forms.Select(
                attrs={"class": "w-full", "placeholder": "請選擇供應商名稱"}
            ),
            "supplier_tel": forms.TextInput(
                attrs={"class": "w-full", "placeholder": "請輸入供應商電話"}
            ),
            "contact_person": forms.TextInput(
                attrs={"class": "w-full", "placeholder": "請輸入聯絡人"}
            ),
            "supplier_email": forms.TextInput(
                attrs={"class": "w-full", "placeholder": "請輸入供應商Email"}
            ),
            "note": forms.Textarea(
                attrs={
                    "class": "w-full",
                    "rows": 3,
                    "placeholder": "請輸入備註",
                }
            ),
        }
        # help_texts = {
        #     "supplier": "請輸入供應商名稱。",
        #     "supplier_tel":"請輸入供應商電話。",
        #     "contact_person":"請輸入聯絡人。",
        #     "supplier_email":"請輸入供應商Email。",
        #     "note": "請輸入備註。",
        # }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False

    def clean(self):
        cleaned_data = super().clean()
        supplier = cleaned_data.get("supplier")
        supplier_tel = cleaned_data.get("supplier_tel")
        contact_person = cleaned_data.get("contact_person")
        supplier_email = cleaned_data.get("supplier_email")
        amount = cleaned_data.get("amount")

        if not supplier:
            self.add_error("supplier", "供應商名稱為必填")
        if supplier_tel == "":
            self.add_error("supplier_tel", "供應商電話為必填")
        elif not re.match(
            r"^(09\d{2}-\d{3}-\d{3}|09\d{8}|09\d{2}-\d{6}|0\d{8}|0\d-\d{7}|0\d-\d{3}-\d{4}|0\d-\d{4}-\d{3})$",
            supplier_tel,
        ):
            self.add_error("supplier_tel", "無效的電話號碼")
        if not contact_person:
            self.add_error("contact_person", "聯絡人為必填")
        if supplier_email == "":
            self.add_error("supplier_email", "供應商Email為必填")
        if amount == 0:
            self.add_error("amount", "請填寫下方採購單細項")

        return cleaned_data


class ProductItemForm(forms.ModelForm):
    class Meta:
        model = ProductItem
        fields = ["product", "quantity", "cost_price", "subtotal"]
        widgets = {
            "product": forms.Select(attrs={"class": "w-full"}),
            "quantity": forms.NumberInput(attrs={"class": "w-full", "min": 1}),
            "cost_price": forms.NumberInput(attrs={"class": "w-full"}),
            "subtotal": forms.NumberInput(attrs={"class": "w-full"}),
        }


ProductItemFormSet = inlineformset_factory(
    PurchaseOrder, ProductItem, form=ProductItemForm, extra=1, can_delete=True
)
