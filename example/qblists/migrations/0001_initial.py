# Generated by Django 4.2.1 on 2023-06-04 02:14

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="OtherNameList",
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
                ("created_on", models.DateTimeField(auto_now_add=True)),
                ("last_update", models.DateTimeField(auto_now=True)),
                (
                    "qbwc_list_id",
                    models.CharField(blank=True, max_length=120, null=True),
                ),
                ("qbwc_time_created", models.DateTimeField(blank=True, null=True)),
                ("qbwc_time_modified", models.DateTimeField(blank=True, null=True)),
                ("name", models.CharField(max_length=60)),
            ],
            options={
                "verbose_name": "Other Names List",
                "verbose_name_plural": "Other Names List",
            },
        ),
    ]