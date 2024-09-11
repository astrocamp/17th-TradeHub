from django.forms import ModelForm

from apps.goods_receipts.models import GoodsReceipt


class GoodsReceiptForm(ModelForm):
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
