import django.db.models.deletion
import django_fsm
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
                ("product_number", models.CharField(max_length=10, unique=True)),
                ("product_name", models.CharField(max_length=20)),
                ("cost_price", models.PositiveIntegerField()),
                ("sale_price", models.PositiveIntegerField()),
                ("note", models.TextField(blank=True, null=True)),
                (
                    "state",
                    django_fsm.FSMField(
                        choices=[
                            ("often", "經常"),
                            ("haply", "偶爾"),
                            ("never", "從不"),
                        ],
                        default="often",
                        max_length=50,
                        protected=True,
                    ),
                ),
                (
                    "supplier",
                    models.ForeignKey(
                        default=0,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="products",
                        to="suppliers.supplier",
                    ),
                ),
            ],
        ),
    ]
