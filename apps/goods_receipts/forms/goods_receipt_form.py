from django import forms

from apps.goods_receipts.models import GoodsReceipt


class FileUploadForm(forms.Form):
    file = forms.FileField()


class GoodsReceiptForm(forms.ModelForm):
    class Meta:
        model = GoodsReceipt
        fields = [
            "receipt_number",
            "supplier",
            "goods_name",
            "quantity",
            "method",
            "date",
            "note",
        ]

        labels = {
            "receipt_number": "進貨單號",
            "supplier": "供應商名稱",
            "goods_name": "貨品名稱",
            "quantity": "數量",
            "method": "運送方式",
            "date": "日期",
            "note": "備註",
        }

        widgets = {
            "receipt_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "請輸入進貨單號",
                }
            ),
            "supplier": forms.Select(
                attrs={
                    "class": "form-control",
                    "type": "select",
                }
            ),
            "goods_name": forms.Select(
                attrs={
                    "class": "form-control",
                    "placeholder": "請輸入貨品名稱",
                }
            ),
            "quantity": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "請輸入數量",
                }
            ),
            "method": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "請輸入運送方式",
                }
            ),
            "date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),
            "note": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "請輸入備註",
                    "rows": 3,
                }
            ),
        }
        help_texts = {
            "receipt_number": "請輸入進貨單號.",
            "supplier": "請輸入供應商名稱.",
            "goods_name": "請輸入貨品名稱.",
            "quantity": "請輸入數量.",
            "method": "請輸入運送方式 (e.g., 'Express Delivery', 'Pick Up').",
            "date": "請輸入日期.",
            "note": "請輸入備註.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False

    def clean(self):
        cleaned_data = super().clean()
        receipt_number = cleaned_data.get("receipt_number")
        supplier = cleaned_data.get("supplier")
        goods_name = cleaned_data.get("goods_name")
        quantity = cleaned_data.get("quantity")
        method = cleaned_data.get("method")
        date = cleaned_data.get("date")

        if not receipt_number:
            self.add_error("receipt_number", "請輸入進貨單號")

        if not supplier:
            self.add_error("supplier", "請輸入供應商名稱")

        if not goods_name:
            self.add_error("goods_name", "請輸入貨品名稱")

        if quantity is None:
            self.add_error("quantity", "請輸入數量")
        elif quantity == 0:
            self.add_error("quantity", "數量不能為0")

        if not method:
            self.add_error("method", "請輸入運送方式")

        if not date:
            self.add_error("date", "請輸入日期")

        return cleaned_data
