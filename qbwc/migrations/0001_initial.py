# Generated by Django 4.2.1 on 2023-06-05 00:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
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
                (
                    "qbid",
                    models.CharField(default=uuid.uuid4, editable=False, max_length=60),
                ),
                (
                    "app_owner_id",
                    models.CharField(default=uuid.uuid4, editable=False, max_length=60),
                ),
                (
                    "app_file_id",
                    models.CharField(default=uuid.uuid4, editable=False, max_length=60),
                ),
                ("file_path", models.CharField(blank=True, max_length=150, null=True)),
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
                    models.CharField(
                        default=uuid.uuid4, editable=False, max_length=60, unique=True
                    ),
                ),
                (
                    "batch_id",
                    models.CharField(
                        default=uuid.uuid4, editable=False, max_length=60, unique=True
                    ),
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
                (
                    "owner",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
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
                    "status",
                    models.CharField(
                        choices=[
                            ("CREATED", "CREATED"),
                            ("SUCCESS", "SUCCESS"),
                            ("FAILED", "FAILED"),
                        ],
                        default="CREATED",
                        max_length=20,
                    ),
                ),
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
                    models.CharField(editable=False, max_length=120, null=True),
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
