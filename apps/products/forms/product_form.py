from django import forms
from django.forms import ModelForm

from apps.products.models import Product


class FileUploadForm(forms.Form):
    file = forms.FileField()


class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = [
            "product_number",
            "product_name",
            "cost_price",
            "sale_price",
            "supplier",
            "note",
        ]
        widgets = {
            "product_number": forms.TextInput(
                attrs={
                    "class": "form-control w-full rounded-md p-2 bg-gray-100",
                    "placeholder": "請輸入商品編號",
                }
            ),
            "product_name": forms.TextInput(
                attrs={
                    "class": "form-control w-full rounded-md p-2 bg-gray-100",
                    "placeholder": "請輸入商品名稱",
                }
            ),
            "cost_price": forms.NumberInput(
                attrs={
                    "class": "form-control w-full rounded-md p-2 bg-gray-100",
                    "placeholder": "請輸入商品進價",
                }
            ),
            "sale_price": forms.NumberInput(
                attrs={
                    "class": "form-control w-full rounded-md p-2 bg-gray-100",
                    "placeholder": "請輸入商品售價",
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
            "product_number": "商品編號",
            "product_name": "商品名稱",
            "cost_price": "進價",
            "sale_price": "售價",
            "supplier": "供應商",
            "note": "備註",
        }
        help_texts = {
            "product_number": "例:P001",
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
        product_number = cleaned_data.get("product_number")
        product_name = cleaned_data.get("product_name")
        cost_price = cleaned_data.get("cost_price")
        sale_price = cleaned_data.get("sale_price")
        supplier = cleaned_data.get("supplier")

        if not product_number:
            self.add_error("product_number", "請填入商品編號")
        elif (
            Product.objects.filter(product_number=product_number)
            .exclude(id=self.instance.id)
            .exists()
        ):
            self.add_error("product_number", "此商品編號已存在")

        if not product_name:
            self.add_error("product_name", "請填入商品名稱")

        if cost_price is None:
            self.add_error("cost_price", "請填入商品進價")
        elif cost_price == 0:
            self.add_error("cost_price", "商品價格應該大於零")

        if sale_price is None:
            self.add_error("sale_price", "請填入商品售價")
        elif sale_price == 0:
            self.add_error("sale_price", "商品價格應該大於零")

        if not supplier:
            self.add_error("supplier", "請選擇供應商名稱")

        return cleaned_data
