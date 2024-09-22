from django import forms

from apps.goods_receipts.models import GoodsReceipt


class GoodsReceiptForm(forms.ModelForm):
    class Meta:
        model = GoodsReceipt
        fields = [
            "receipt_number",
            "supplier",
            "goods_name",
            "order_quantity",
            "purchase_quantity",
            "method",
            "date",
            "note",
        ]

        labels = {
            "receipt_number": "進貨單號",
            "supplier": "供應商名稱",
            "goods_name": "貨品名稱",
            "order_quantity": "訂購數量",
            "purchase_quantity": "進貨數量",
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
            "order_quantity": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "請輸入數量",
                }
            ),
            "purchase_quantity": forms.NumberInput(
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
            "order_quantity": "請輸入訂購數量.",
            "purchase_quantity": "請輸入進貨數量.",
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
        order_quantity = cleaned_data.get("order_quantity")
        purchase_quantity = cleaned_data.get("purchase_quantity")
        method = cleaned_data.get("method")
        date = cleaned_data.get("date")

        if not receipt_number:
            self.add_error("receipt_number", "請輸入進貨單號")

        if not supplier:
            self.add_error("supplier", "請輸入供應商名稱")

        if not goods_name:
            self.add_error("goods_name", "請輸入貨品名稱")

        if order_quantity is None:
            self.add_error("order_quantity", "請輸入訂購數量")
        elif order_quantity == 0:
            self.add_error("order_quantity", "訂購數量不能為0")

        if purchase_quantity is None:
            self.add_error("purchase_quantity", "請輸入進貨數量")
        elif purchase_quantity == 0:
            self.add_error("purchase_quantity", "進貨數量不能為0")

        if not method:
            self.add_error("method", "請輸入運送方式")

        if not date:
            self.add_error("date", "請輸入日期")

        return cleaned_data
