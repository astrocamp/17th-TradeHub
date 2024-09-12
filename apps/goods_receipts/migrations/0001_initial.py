import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("products", "0001_initial"),
        ("suppliers", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="GoodsReceipt",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("receipt_number", models.CharField(max_length=10, unique=True)),
                ("quantity", models.PositiveIntegerField()),
                ("method", models.CharField(max_length=20)),
                ("date", models.DateField(default=django.utils.timezone.now)),
                ("note", models.TextField()),
                (
                    "goods_name",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="goods_receipts",
                        to="products.product",
                    ),
                ),
                (
                    "supplier",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="goods_receipts",
                        to="suppliers.supplier",
                    ),
                ),
            ],
        ),
    ]
