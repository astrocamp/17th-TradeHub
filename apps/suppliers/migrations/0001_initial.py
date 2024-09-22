import django.utils.timezone
import django_fsm
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
                ("name", models.CharField(max_length=20)),
                ("telephone", models.CharField(max_length=15)),
                ("contact_person", models.CharField(max_length=20)),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("gui_number", models.CharField(max_length=8, unique=True)),
                ("address", models.TextField()),
                ("create_at", models.DateTimeField(auto_now_add=True)),
                ("note", models.TextField(blank=True, null=True)),
                (
                    "state",
                    django_fsm.FSMField(
                        choices=[
                            ("often", "經常"),
                            ("haply", "偶爾"),
                            ("never", "從不"),
                        ],
                        default="never",
                        max_length=50,
                        protected=True,
                    ),
                ),
            ],
        ),
    ]
