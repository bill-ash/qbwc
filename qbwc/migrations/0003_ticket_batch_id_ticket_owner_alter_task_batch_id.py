# Generated by Django 4.2.1 on 2023-05-08 04:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("qbwc", "0002_remove_baseobjectmixin_batch_status_task_batch_id_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="ticket",
            name="batch_id",
            field=models.CharField(default=uuid.uuid4, editable=False, max_length=60),
        ),
        migrations.AddField(
            model_name="ticket",
            name="owner",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="task",
            name="batch_id",
            field=models.CharField(max_length=60, null=True),
        ),
    ]
