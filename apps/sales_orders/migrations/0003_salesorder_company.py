<<<<<<<< HEAD:apps/sales_orders/migrations/0002_salesorder_company.py
# Generated by Django 5.1.1 on 2024-09-22 18:10
========
# Generated by Django 5.1.1 on 2024-09-23 16:09
>>>>>>>> 6bea46e045d7b1c7cbdd934606d2bcd524ffbb41:apps/sales_orders/migrations/0003_salesorder_company.py

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
<<<<<<<< HEAD:apps/sales_orders/migrations/0002_salesorder_company.py
        ("company", "0006_remove_company_company_id"),
        ("sales_orders", "0001_initial"),
========
        ("company", "0009_auto_20240923_1948"),
        ("sales_orders", "0002_alter_salesorder_order_number"),
>>>>>>>> 6bea46e045d7b1c7cbdd934606d2bcd524ffbb41:apps/sales_orders/migrations/0003_salesorder_company.py
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