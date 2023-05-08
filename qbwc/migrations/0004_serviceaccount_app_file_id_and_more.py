# Generated by Django 4.2.1 on 2023-05-08 04:31

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("qbwc", "0003_ticket_batch_id_ticket_owner_alter_task_batch_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="serviceaccount",
            name="app_file_id",
            field=models.CharField(default=uuid.uuid4, editable=False, max_length=60),
        ),
        migrations.AddField(
            model_name="serviceaccount",
            name="app_owner_id",
            field=models.CharField(default=uuid.uuid4, editable=False, max_length=60),
        ),
    ]