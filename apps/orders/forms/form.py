from django import forms

from apps.orders.models import Orders


class FileUploadForm(forms.Form):
    file = forms.FileField()


class OrderForm(forms.ModelForm):
    class Meta:
        model = Orders
        fields = "__all__"

        widgets = {
            "code": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "請輸入訂單編號"}
            ),
            "client": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
            "product": forms.Select(
                attrs={
                    "class": "form-control",
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
            "code": "請輸入訂單編號",
            "client": "請選擇客戶",
            "product": "請選擇產品",
            "note": "請輸入備註",
        }

        labels = {
            "code": "訂單編號",
            "client": "客戶",
            "product": "產品",
            "note": "備註",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False

    def clean(self):
        cleaned_data = super().clean()
        code = cleaned_data.get("code")
        client = cleaned_data.get("client")
        product = cleaned_data.get("product")

        if not code:
            self.add_error("code", "訂單編號是必填的")

        if not client:
            self.add_error("client", "客戶是必填的")

        if not product:
            self.add_error("product", "產品是必填的")

        return cleaned_data
