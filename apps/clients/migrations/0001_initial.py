import django_fsm
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Client",
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
                ("phone_number", models.CharField(max_length=15)),
                ("address", models.CharField(max_length=150)),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("create_at", models.DateTimeField(auto_now_add=True)),
                ("delete_at", models.DateTimeField(auto_now=True)),
                ("note", models.TextField(blank=True, max_length=150, null=True)),
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
