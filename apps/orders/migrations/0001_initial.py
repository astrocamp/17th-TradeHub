# Generated by Django 5.1 on 2024-09-04 06:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("clients", "0001_initial"),
        ("products", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Orders",
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
                ("code", models.CharField(max_length=15)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("deleted_at", models.DateTimeField(blank=True, null=True)),
                ("note", models.TextField(blank=True)),
                (
                    "client_fk",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, to="clients.client"
                    ),
                ),
                (
                    "product_fk",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="products.product",
                    ),
                ),
            ],
        ),
    ]
