# Generated by Django 4.2.1 on 2023-06-04 16:50

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("vendors", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="vendor",
            name="is_active",
            field=models.BooleanField(default=True),
        ),
    ]
