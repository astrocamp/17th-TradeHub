import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("suppliers", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Product",
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
                ("product_id", models.CharField(max_length=10)),
                ("product_name", models.CharField(max_length=20)),
                ("price", models.IntegerField()),
                ("note", models.TextField()),
                (
                    "supplier",
                    models.ForeignKey(
                        default=0,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="products",
                        to="suppliers.supplier",
                    ),
                ),
            ],
        ),
    ]