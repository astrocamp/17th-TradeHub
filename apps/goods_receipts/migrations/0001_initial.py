# Generated by Django 5.1.1 on 2024-09-17 17:41

import django.db.models.deletion
import django.utils.timezone
import django_fsm
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("products", "0002_alter_product_state"),
        ("suppliers", "0002_alter_supplier_state"),
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
                ("order_quantity", models.PositiveIntegerField()),
                ("purchase_quantity", models.PositiveIntegerField(null=True)),
                ("method", models.CharField(max_length=20)),
                ("date", models.DateField(default=django.utils.timezone.now)),
                ("note", models.TextField()),
                ("deleted_at", models.DateTimeField(blank=True, null=True)),
                (
                    "state",
                    django_fsm.FSMField(
                        choices=[
                            ("to_be_restocked", "待進貨"),
                            ("to_be_stocked", "待入庫"),
                            ("finished", "完成"),
                        ],
                        default="to_be_restocked",
                        max_length=50,
                        protected=True,
                    ),
                ),
                ("is_finished", models.BooleanField(default=False)),
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
