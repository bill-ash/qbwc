# Generated by Django 4.2.1 on 2023-05-17 03:40

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0003_alter_glaccount_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="glaccount",
            name="full_name",
            field=models.CharField(max_length=120, unique=True),
        ),
        migrations.AlterField(
            model_name="glaccount",
            name="name",
            field=models.CharField(max_length=120, unique=True),
        ),
    ]
