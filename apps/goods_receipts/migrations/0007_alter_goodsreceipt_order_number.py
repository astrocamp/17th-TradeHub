# Generated by Django 5.1.1 on 2024-09-29 15:40

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("goods_receipts", "0006_alter_goodsreceipt_user"),
    ]

    operations = [
        migrations.AlterField(
            model_name="goodsreceipt",
            name="order_number",
            field=models.CharField(max_length=20),
        ),
    ]
