# Generated by Django 5.1 on 2024-08-29 05:03

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Supplier",
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
                ("name", models.CharField(max_length=100)),
                ("tel", models.CharField(max_length=20)),
                ("contact", models.CharField(max_length=100)),
                ("GUInumber", models.IntegerField(unique=True)),
                ("address", models.TextField()),
                ("remark", models.TextField(blank=True, null=True)),
            ],
        ),
    ]
