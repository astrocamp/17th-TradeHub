# Generated by Django 5.1.1 on 2024-09-16 17:56

import django_fsm
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("clients", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="client",
            name="state",
            field=django_fsm.FSMField(
                choices=[
                    ("often", "經常購買"),
                    ("haply", "偶爾購買"),
                    ("never", "從不購買"),
                ],
                default="never",
                max_length=50,
                protected=True,
            ),
        ),
    ]