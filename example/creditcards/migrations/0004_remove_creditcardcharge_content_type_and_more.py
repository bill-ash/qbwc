# Generated by Django 4.2.1 on 2023-06-04 23:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("qblists", "0002_alter_othernamelist_name"),
        ("creditcards", "0003_rename_vendor_creditcardcharge_content_type"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="creditcardcharge",
            name="content_type",
        ),
        migrations.RemoveField(
            model_name="creditcardcharge",
            name="object_id",
        ),
        migrations.AddField(
            model_name="creditcardcharge",
            name="vendor",
            field=models.ForeignKey(
                default="",
                on_delete=django.db.models.deletion.CASCADE,
                to="qblists.othernamelist",
            ),
            preserve_default=False,
        ),
    ]