# Generated by Django 5.1.1 on 2024-09-08 14:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="orders",
            name="deleted_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
