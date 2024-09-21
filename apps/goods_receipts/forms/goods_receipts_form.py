import re

from django import forms
from django.forms import inlineformset_factory

from apps.goods_receipts.models import GoodsReceipt, GoodsReceiptProductItem


class FileUploadForm(forms.Form):
    file = forms.FileField()


class GoodsReceiptForm(forms.ModelForm):
    class Meta:
        model = GoodsReceipt
        fields = [
            "supplier",
            "supplier_tel",
            "contact_person",
            "supplier_email",
            "receiving_method",
            "amount",
            "note",
        ]
        labels = {
            "supplier": "供應商名稱",
            "supplier_tel": "供應商電話",
            "contact_person": "聯絡人",
            "supplier_email": "供應商Email",
            "note": "備註",
            "amount": "總金額",
            "receiving_method": "運送方式",
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
            "receiving_method": forms.Select(
                attrs={
                    "class": "w-full",
                    "placeholder": "請輸入運送方式",
                }
            ),
        }
        # help_texts = {
        #     "supplier": "請輸入供應商名稱。",
        #     "supplier_tel":"請輸入供應商電話。",
        #     "contact_person":"請輸入聯絡人。",
        #     "supplier_email":"請輸入供應商Email。",
        #     "note": "請輸入備註。",
        #     "receiving_method":"自取，貨運。",
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
        receiving_method = cleaned_data.get("receiving_method")

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
            self.add_error("amount", "請填寫下方進貨單細項")
        if not receiving_method:
            self.add_error("receiving_method", "運送方式為必填")

        return cleaned_data


class GoodsReceiptProductItemForm(forms.ModelForm):
    class Meta:
        model = GoodsReceiptProductItem
        fields = [
            "product",
            "ordered_quantity",
            "received_quantity",
            "cost_price",
            "subtotal",
        ]
        widgets = {
            "product": forms.Select(attrs={"class": "w-full"}),
            "ordered_quantity": forms.NumberInput(attrs={"class": "w-full", "min": 1}),
            "received_quantity": forms.NumberInput(attrs={"class": "w-full", "min": 1}),
            "cost_price": forms.NumberInput(attrs={"class": "w-full"}),
            "subtotal": forms.NumberInput(attrs={"class": "w-full"}),
        }


ProductItemFormSet = inlineformset_factory(
    GoodsReceipt,
    GoodsReceiptProductItem,
    form=GoodsReceiptProductItemForm,
    extra=1,
    can_delete=True,
)
