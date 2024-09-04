import django.utils.timezone
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
                ("name", models.CharField(blank=True, max_length=100)),
                ("telephone", models.CharField(blank=True, max_length=10)),
                ("contact_person", models.CharField(max_length=100)),
                ("email", models.CharField(blank=True, max_length=254)),
                ("gui_number", models.CharField(blank=True, max_length=8, unique=True)),
                ("address", models.TextField(blank=True)),
                (
                    "established_date",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                ("note", models.TextField(blank=True)),
            ],
        ),
    ]