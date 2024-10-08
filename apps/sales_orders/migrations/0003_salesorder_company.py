# Generated by Django 5.1.1 on 2024-09-23 16:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("company", "0009_auto_20240923_1948"),
        ("sales_orders", "0002_alter_salesorder_order_number"),
    ]

    operations = [
        migrations.AddField(
            model_name="salesorder",
            name="company",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="sales_orders",
                to="company.company",
            ),
        ),
    ]
