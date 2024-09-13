from django import forms

from ..models import Inventory


class RestockForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = [
            "product",
            "supplier",
            "quantity",
            "safety_stock",
            "note",
        ]

        widgets = {
            "product": forms.Select(
                attrs={
                    "class": "h-[24px] w-full rounded-md p-2 flex items-center justify-center bg-gray-100 focus:outline-none text-sm",
                    "readonly": "readonly",
                }
            ),
            "supplier": forms.Select(
                attrs={
                    "class": "h-[24px] w-full rounded-md p-2 flex items-center justify-center bg-gray-100 focus:outline-none text-sm",
                    "readonly": "readonly",
                }
            ),
            "quantity": forms.NumberInput(
                attrs={
                    "class": "form-control w-full rounded-md p-2 bg-gray-100",
                    "placeholder": "請輸入現有庫存數量",
                }
            ),
            "safety_stock": forms.NumberInput(
                attrs={
                    "class": "form-control w-full rounded-md p-2 bg-gray-100",
                    "placeholder": "請輸入安全庫存數量",
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
        help_texts = {
            "product": "請選擇產品",
            "supplier": "請選擇供應商",
            "quantity": "請填入數字即可",
            "safety_stock": "請填入數字即可",
            "note": "",
        }
        labels = {
            "product": "產品名稱",
            "supplier": "供應商名稱",
            "quantity": "現有庫存數量",
            "safety_stock": "安全庫存數量",
            "note": "備註",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False

    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get("product")
        supplier = cleaned_data.get("supplier")
        quantity = cleaned_data.get("quantity")
        safety_stock = cleaned_data.get("safety_stock")

        if not product:
            self.add_error("product", "請選擇產品")

        if not supplier:
            self.add_error("supplier", "請選擇供應商")

        if quantity is None:
            self.add_error("quantity", "請輸入現有庫存數量")

        if safety_stock is None:
            self.add_error("safety_stock", "請輸入安全庫存數量")

        return cleaned_data
