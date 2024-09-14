from django import forms

from apps.goods_receipts.models import GoodsReceipt


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
                    "placeholder": "Enter receipt number",
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
                    "placeholder": "Enter goods name",
                }
            ),
            "quantity": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter quantity",
                }
            ),
            "method": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter method",
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
                    "placeholder": "Any additional notes.",
                    "rows": 3,
                }
            ),
        }
        help_texts = {
            "receipt_number": "Enter the receipt number.",
            "supplier": "Enter the full name of the supplier.",
            "goods_name": "Enter the goods name.",
            "quantity": "Enter the quantity",
            "method": "Enter the delivery method (e.g., 'Express Delivery', 'Pick Up').",
            "date": "Enter the date.",
            "note": "Enter any additional notes.",
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
            self.add_error("receipt_number", "Receipt number is required.")

        if not supplier:
            self.add_error("supplier", "Supplier is required.")

        if not goods_name:
            self.add_error("goods_name", "Goods name is required.")

        if quantity is None:
            self.add_error("quantity", "Quantity is required.")
        elif quantity == 0:
            self.add_error("quantity", "Quantity should not be 0.")

        if not method:
            self.add_error("method", "Method is required.")

        if not date:
            self.add_error("date", "Date is required.")

        return cleaned_data
