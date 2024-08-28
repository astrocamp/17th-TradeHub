from django.forms import ModelForm

from apps.products.models import Product


class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = ["productNumber", "title", "price", "quantity", "note"]
