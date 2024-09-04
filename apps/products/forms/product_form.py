from django.forms import ModelForm, Select

from apps.products.models import Product


class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = ["product_id", "product_name", "price", "supplier", "note"]
        widgets = {
            "supplier": Select(
                attrs={
                    "class": "form-control w-full select select-bordered flex items-center justify-center"
                }
            )
        }
