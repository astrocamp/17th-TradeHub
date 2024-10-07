import re

from django import forms
from django.forms import inlineformset_factory
from django.forms.models import BaseInlineFormSet

from apps.clients.models import Client
from apps.orders.models import Order, OrderProductItem, Product


class FileUploadForm(forms.Form):
    file = forms.FileField()


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            "client",
            "client_tel",
            "client_address",
            "client_email",
            "note",
            "amount",
        ]
        labels = {
            "client": "客戶名稱",
            "client_tel": "客戶電話",
            "client_address": "客戶地址",
            "client_email": "客戶Email",
            "note": "備註",
            "amount": "總金額",
        }
        widgets = {
            "client": forms.Select(
                attrs={"class": "w-full", "placeholder": "請選擇客戶名稱"}
            ),
            "client_tel": forms.TextInput(
                attrs={"class": "w-full", "placeholder": "請輸入客戶電話"}
            ),
            "client_address": forms.TextInput(
                attrs={"class": "w-full", "placeholder": "請輸入客戶地址"}
            ),
            "client_email": forms.TextInput(
                attrs={"class": "w-full", "placeholder": "請輸入客戶Email"}
            ),
            "note": forms.Textarea(
                attrs={
                    "class": "w-full",
                    "rows": 3,
                    "placeholder": "請輸入備註",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if self.user:
            self.fields["client"].queryset = Client.objects.filter(user=self.user)

        for field in self.fields.values():
            field.required = False

    def clean(self):
        cleaned_data = super().clean()
        client = cleaned_data.get("client")
        client_tel = cleaned_data.get("client_tel")
        client_address = cleaned_data.get("client_address")
        client_email = cleaned_data.get("client_email")
        amount = cleaned_data.get("amount")

        if not client:
            self.add_error("client", "客戶名稱為必填")
        if client_tel == "":
            self.add_error("client_tel", "客戶電話為必填")
        elif not re.match(
            r"^(09\d{2}-\d{3}-\d{3}|09\d{8}|09\d{2}-\d{6}|0\d{8}|0\d-\d{7}|0\d-\d{3}-\d{4}|0\d-\d{4}-\d{3})$",
            client_tel,
        ):
            self.add_error("client_tel", "無效的電話號碼")
        if not client_address:
            self.add_error("client_address", "客戶地址為必填")
        if client_email == "":
            self.add_error("client_email", "客戶Email為必填")
        if amount == 0:
            self.add_error("amount", "請填寫下方訂購單細項")

        return cleaned_data


class OrderProductItemForm(forms.ModelForm):
    class Meta:
        model = OrderProductItem
        fields = [
            "product",
            "stock_quantity",
            "ordered_quantity",
            "sale_price",
            "subtotal",
        ]
        widgets = {
            "product": forms.Select(attrs={"class": "w-full"}),
            "stock_quantity": forms.Select(attrs={"class": "w-full"}),
            "ordered_quantity": forms.NumberInput(attrs={"class": "w-full", "min": 1}),
            "sale_price": forms.NumberInput(attrs={"class": "w-full"}),
            "subtotal": forms.NumberInput(attrs={"class": "w-full"}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if self.user:
            self.fields["product"].queryset = Product.objects.filter(user=self.user)


class BaseOrderProductItemFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        for form in self.forms:
            form.user = self.user
            if self.user:
                form.fields["product"].queryset = Product.objects.filter(user=self.user)

    def _construct_form(self, i, **kwargs):
        form = super()._construct_form(i, **kwargs)
        form.user = self.user
        return form


OrderProductItemFormSet = inlineformset_factory(
    Order,
    OrderProductItem,
    form=OrderProductItemForm,
    formset=BaseOrderProductItemFormSet,
    extra=1,
    can_delete=True,
)
