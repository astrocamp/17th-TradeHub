# Generated by Django 5.1 on 2024-09-01 17:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("clients", "0002_alter_client_create_at_alter_client_delete_at_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="client",
            name="phone_number",
            field=models.CharField(max_length=15),
        ),
    ]