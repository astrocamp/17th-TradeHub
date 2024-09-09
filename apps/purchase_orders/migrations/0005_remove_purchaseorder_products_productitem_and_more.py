# Generated by Django 5.1.1 on 2024-09-09 08:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0001_initial"),
        ("purchase_orders", "0004_alter_purchaseorder_total_amount_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="purchaseorder",
            name="products",
        ),
        migrations.CreateModel(
            name="ProductItem",
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
                ("quantity", models.PositiveIntegerField()),
                ("price", models.PositiveIntegerField()),
                ("subtotal", models.PositiveIntegerField()),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="products.product",
                    ),
                ),
                (
                    "purchase_order",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="items",
                        to="purchase_orders.purchaseorder",
                    ),
                ),
            ],
        ),
        migrations.DeleteModel(
            name="PurchaseOrderProduct",
        ),
    ]
