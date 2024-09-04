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
                ("name", models.CharField(max_length=30)),
                ("phone_number", models.CharField(max_length=15)),
                ("address", models.CharField(max_length=150)),
                ("email", models.EmailField(max_length=254)),
                ("create_at", models.DateTimeField(auto_now_add=True)),
                ("delete_at", models.DateTimeField(auto_now=True)),
                ("note", models.TextField(max_length=150, null=True)),
            ],
        ),
    ]
