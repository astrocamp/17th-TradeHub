from django import forms
from django.forms import ModelForm

from apps.products.models import Product


class FileUploadForm(forms.Form):
    file = forms.FileField()


class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = [
            "product_id",
            "product_name",
            "cost_price",
            "sale_price",
            "supplier",
            "note",
        ]
        widgets = {
            "product_id": forms.TextInput(
                attrs={
                    "class": "form-control w-full rounded-md p-2 bg-gray-100",
                    "placeholder": "請輸入產品編號",
                }
            ),
            "product_name": forms.TextInput(
                attrs={
                    "class": "form-control w-full rounded-md p-2 bg-gray-100",
                    "placeholder": "請輸入產品名稱",
                }
            ),
            "cost_price": forms.NumberInput(
                attrs={
                    "class": "form-control w-full rounded-md p-2 bg-gray-100",
                    "placeholder": "請輸入產品成本價",
                }
            ),
            "prcie_price": forms.NumberInput(
                attrs={
                    "class": "form-control w-full rounded-md p-2 bg-gray-100",
                    "placeholder": "請輸入產品售價",
                }
            ),
            "supplier": forms.Select(
                attrs={
                    "class": "h-[24px] w-full rounded-md p-2 flex items-center justify-center bg-gray-100 focus:outline-none text-sm"
                }
            ),
            "note": forms.Textarea(
                attrs={
                    "class": "form-control w-full rounded-md p-2 bg-gray-100 text-sm",
                    "placeholder": "如有其他備註事項，請填入",
                    "rows": 3,
                }
            ),
        }
        labels = {
            "product_id": "產品編號",
            "product_name": "產品名稱",
            "cost_price": "成本價",
            "sale_price": "售價",
            "supplier": "供應商",
            "note": "備註",
        }
        help_texts = {
            "product_id": "例:P001",
            "product_name": "例:小黑板",
            "cost_price": "請填入數字即可",
            "sale_price": "售價應高於成本價",
            "supplier": "請選擇供應商",
            "note": "",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False

    def clean(self):
        cleaned_data = super().clean()
        product_id = cleaned_data.get("product_id")
        product_name = cleaned_data.get("product_name")
        cost_price = cleaned_data.get("cost_price")
        sale_price = cleaned_data.get("sale_price")
        supplier = cleaned_data.get("supplier")

        if not product_id:
            self.add_error("product_id", "請填入產品編號")
        elif (
            Product.objects.filter(product_id=product_id)
            .exclude(id=self.instance.id)
            .exists()
        ):
            self.add_error("product_id", "此產品編號已存在")

        if not product_name:
            self.add_error("product_name", "請填入產品名稱")

        if cost_price is None:
            self.add_error("price", "請填入產品價格")
        elif cost_price == 0:
            self.add_error("price", "產品價格應該大於零")

        if sale_price is None:
            self.add_error("price", "請填入產品價格")
        elif sale_price == 0:
            self.add_error("price", "產品價格應該大於零")

        if not supplier:
            self.add_error("supplier", "請選擇供應商")

        return cleaned_data
