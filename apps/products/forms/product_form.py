from django.forms import ModelForm, SelectMultiple

from apps.products.models import Product


class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = ["product_id", "product_name", "price", "supplier", "note"]
        widgets = {
            "supplier": SelectMultiple(
                attrs={
                    "class": "form-control w-full select select-bordered flex items-center justify-center"
                }
            )
        }
