from django import forms

from apps.sales_orders.models import SalesOrder


class FileUploadForm(forms.Form):
    file = forms.FileField()


class SalesOrderForm(forms.ModelForm):
    class Meta:
        model = SalesOrder
        fields = [
            "client",
            "product",
            "quantity",
            "stock",
            "price",
        ]

        labels = {
            "client": "客戶名稱",
            "product": "商品名稱",
            "quantity": "數量",
            "stock": "庫存",
            "price": "價格",
        }

        widgets = {
            "client": forms.Select(
                attrs={
                    "class": "form-control w-full select select-bordered flex items-center justify-center"
                }
            ),
            "product": forms.Select(
                attrs={
                    "class": "form-control w-full select select-bordered flex items-center justify-center"
                }
            ),
            "quantity": forms.NumberInput(
                attrs={
                    "class": "form-control w-full input input-bordered flex items-center justify-center"
                }
            ),
            "stock": forms.Select(
                attrs={
                    "class": "form-control w-full select select-bordered flex items-center justify-center"
                }
            ),
            "price": forms.NumberInput(
                attrs={
                    "class": "form-control w-full input input-bordered flex items-center justify-center"
                }
            ),
        }
        help_texts = {
            "client": "請選擇客戶。",
            "product": "請選擇商品。",
            "quantity": "請輸入數量。",
            "stock": "請選擇庫存。",
            "price": "請輸入價格。",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False

    def clean(self):
        cleaned_data = super().clean()
        client = cleaned_data.get("client")
        product = cleaned_data.get("product")
        quantity = cleaned_data.get("quantity")
        stock = cleaned_data.get("stock")
        price = cleaned_data.get("price")

        if not client:
            self.add_error("client", "請選擇客戶。")

        if not product:
            self.add_error("product", "請選擇商品。")

        if quantity is None:
            self.add_error("quantity", "請輸入數量。")
        elif quantity == 0:
            self.add_error("quantity", "數量不能為零。")

        if not stock:
            self.add_error("stock", "請選擇庫存。")

        if price is None:
            self.add_error("price", "請輸入價格。")
        elif price == 0:
            self.add_error("price", "價格不能為零。")

        return cleaned_data
