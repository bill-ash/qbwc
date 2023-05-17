# Generated by Django 4.2.1 on 2023-05-16 23:21

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="GlAccount",
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
                ("batch_id", models.CharField(blank=True, max_length=60, null=True)),
                (
                    "qbwc_list_id",
                    models.CharField(blank=True, max_length=120, null=True),
                ),
                ("qbwc_time_created", models.DateTimeField(blank=True, null=True)),
                ("qbwc_time_modified", models.DateTimeField(blank=True, null=True)),
                ("name", models.CharField(max_length=60)),
                ("full_name", models.CharField(max_length=60, unique=True)),
                ("description", models.TextField(blank=True, null=True)),
                ("account_type", models.CharField(max_length=50)),
                ("account_number", models.CharField(max_length=40, unique=True)),
                ("is_active", models.BooleanField(default=True)),
                ("help_name", models.CharField(blank=True, max_length=30, null=True)),
                ("help_description", models.TextField(blank=True, null=True)),
                ("display", models.BooleanField(default=True)),
            ],
            options={
                "verbose_name": "GL Account",
                "verbose_name_plural": "GL Accounts",
            },
        ),
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
                ("batch_id", models.CharField(blank=True, max_length=60, null=True)),
                (
                    "qbwc_list_id",
                    models.CharField(blank=True, max_length=120, null=True),
                ),
                ("qbwc_time_created", models.DateTimeField(blank=True, null=True)),
                ("qbwc_time_modified", models.DateTimeField(blank=True, null=True)),
                ("name", models.CharField(max_length=60)),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
