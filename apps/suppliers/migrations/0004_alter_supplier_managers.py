# Generated by Django 5.1.1 on 2024-09-21 10:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        (
            "suppliers",
            "0003_alter_supplier_managers_remove_supplier_delete_at_and_more",
        ),
    ]

    operations = [
        migrations.AlterModelManagers(
            name="supplier",
            managers=[],
        ),
    ]