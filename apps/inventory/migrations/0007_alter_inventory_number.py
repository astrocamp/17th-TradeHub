# Generated by Django 5.1.1 on 2024-10-02 12:36

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("inventory", "0006_inventory_user"),
    ]

    operations = [
        migrations.AlterField(
            model_name="inventory",
            name="number",
            field=models.CharField(max_length=20),
        ),
    ]
