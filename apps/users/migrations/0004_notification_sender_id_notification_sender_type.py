# Generated by Django 5.1.1 on 2024-09-22 02:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0003_notification_alter_customuser_note_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="notification",
            name="sender_id",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="notification",
            name="sender_type",
            field=models.CharField(default="", max_length=20),
        ),
    ]