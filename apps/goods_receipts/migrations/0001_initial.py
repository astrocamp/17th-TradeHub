# Generated by Django 5.1 on 2024-08-30 03:58

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
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
                ("receipt_number", models.CharField(max_length=10)),
                ("goods_name", models.CharField(max_length=20)),
                ("quantity", models.IntegerField()),
                ("method", models.CharField(max_length=20)),
                ("date", models.DateField(default=django.utils.timezone.now)),
                ("note", models.TextField()),
                (
                    "supplier",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="goods_receipts",
                        to="suppliers.supplier",
                    ),
                ),
            ],
        ),
    ]