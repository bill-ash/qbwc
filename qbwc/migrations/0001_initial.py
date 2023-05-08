# Generated by Django 4.2.1 on 2023-05-07 23:18

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="BaseObjectMixin",
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
                    "batch_status",
                    models.CharField(
                        choices=[("BATCHED", "BATCHED"), ("UN_BATCHED", "UN_BATCHED")],
                        default="UN_BATCHED",
                        max_length=20,
                    ),
                ),
                ("batch_id", models.CharField(blank=True, max_length=60, null=True)),
                ("qb_list_id", models.CharField(blank=True, max_length=120, null=True)),
                ("qb_time_created", models.DateTimeField(blank=True, null=True)),
                ("qb_time_modified", models.DateTimeField(blank=True, null=True)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="ServiceAccount",
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
                ("app_name", models.CharField(max_length=30)),
                (
                    "app_url",
                    models.CharField(default="http://localhost:8000", max_length=150),
                ),
                ("app_description", models.CharField(max_length=30)),
                ("file_path", models.CharField(blank=True, max_length=150, null=True)),
                (
                    "qbid",
                    models.CharField(default=uuid.uuid4, editable=False, max_length=60),
                ),
                ("password", models.CharField(default="test", max_length=120)),
                ("is_active", models.BooleanField(default=True)),
                ("config", models.TextField(blank=True, null=True)),
            ],
            options={
                "verbose_name": "Service Account",
                "verbose_name_plural": "Service Acounts",
            },
        ),
        migrations.CreateModel(
            name="Ticket",
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
                    "ticket",
                    models.CharField(default=uuid.uuid4, editable=False, max_length=60),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("200", "Created"),
                            ("204", "Approved"),
                            ("300", "Processing"),
                            ("201", "Success"),
                            ("500", "Failed"),
                        ],
                        default="200",
                        max_length=3,
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Task",
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
                    "method",
                    models.CharField(
                        choices=[
                            ("GET", "GET"),
                            ("POST", "POST"),
                            ("PATCH", "PATCH"),
                            ("VOID", "VOID"),
                            ("DELETE", "DELETE"),
                        ],
                        default="GET",
                        max_length=6,
                    ),
                ),
                ("model", models.CharField(max_length=90)),
                (
                    "model_instance",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="qbwc.baseobjectmixin",
                    ),
                ),
                (
                    "ticket",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tasks",
                        to="qbwc.ticket",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
