from django.forms import ModelForm

from apps.products.models import Product


class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = ["product_id", "product_name", "price", "supplier", "note"]
