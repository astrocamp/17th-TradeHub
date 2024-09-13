# Generated by Django 5.1.1 on 2024-09-12 06:30

import django_fsm
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("goods_receipts", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="goodsreceipt",
            name="deleted_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="goodsreceipt",
            name="state",
            field=django_fsm.FSMField(
                choices=[("unfinish", "未完成"), ("finished", "完成")],
                default="unfinish",
                max_length=50,
                protected=True,
            ),
        ),
    ]